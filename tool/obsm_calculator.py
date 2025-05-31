import pandas as pd
from logging import getLogger

logger = getLogger(__name__)


def sslc(data: [str, pd.Series]):
    if isinstance(data, str):
        return data.strip().lower()
    else:
        return data.str.strip().str.lower()

# The location of the spell effect data sheet
fp = "C:\\Users\\Frank\\PycharmProjects\\OBSM\\data\\obsm_effs.xlsx"
# skill level: max magicka cost craftable
skill_reqs = {0: 26,  # Magicka < 26: no skill level requirement
              25: 63,  # 26 ≤ Magicka < 63: requires skill of 25
              50: 150,  # 63 ≤ Magicka < 150: requires skill of 50
              75: 400,  # 150 ≤ Magicka < 400: requires skill of 75
              100: 2147483647}  # Magicka ≥ 400: requires skill of 100
def_string = "None"
def_int = 0
no_mag_default = 5

def has_details(eff_name):
    return True if "Skill" in eff_name or "Attribute" in eff_name else False

def has_mag(eff_name):
    no_mag_keys = ["Water", "Bound", "Summon", "Paralyze", "Silence", "Invisibility",
                   "Soul Trap", "Cure"]
    return False if True in [key in eff_name for key in no_mag_keys] else True


class Effect:
    """

    """
    def __init__(self, **kwargs):
        """
        :param data: pd.Series,
        :param details: str, default "None"
        :param mag: int, default 0,
        :param dur: int, default 0
        :param area: int, default 0
        :param range: str, default "None"
        """
        # Base effect data
        data = kwargs.get("data", {})
        self.name = data.get("Effect Name", def_string)
        self.school = data.get("School", def_string)
        self.base = data.get("Base Cost", def_int)
        # Instance data
        self.details = kwargs.get("details", def_string)
        self.mag = kwargs.get("mag", def_int) if has_mag(self.name) else no_mag_default
        self.dur = kwargs.get("dur", def_int)
        self.area = kwargs.get("area", def_int)
        self.range = kwargs.get("range", def_string)
        # Derived values
        self.is_target = True if self.range == "Target" else False
        self.eff_cost = self._calc_eff_cost()

    def __str__(self):
        summary = ''
        eff_name_txt =  self.name + (f": {self.details}" if has_details(self.name) else "")
        summary += (eff_name_txt + " ")
        summary += f"{self.mag} points " if has_mag(self.name) else ""
        summary += f"in {self.area} feet " if self.area > 0 else ""
        summary += f"for {self.dur} seconds "
        summary += f"on {self.range}"
        return summary

    def _calc_eff_cost(self):
        """
        B = Base Cost / 10
        M = Magnitude ^ 1.28
        D = Duration
        A = Area × 0.15
        Total cost = B × M × D × A

        If M, D, or A is less than 1, a value of 1 should be used.
        The magicka cost is further multiplied by 1.5 if the spell is a Targeted spell.
        """
        # Check if effect is initialized or not
        if self.name == def_string:
            return def_int
        # Effect has been set up with some non-default data
        eff_cost = (self.base / 10.0 *
                    max(pow(self.mag, 1.28), 1.0) *
                    max(self.dur, 1) *
                    max(self.area * 0.15, 1) *
                    (1.5 if self.is_target else 1))
        return round(eff_cost, 2)

    def set_param(self, **kwargs):
        """
        Updates mag, dur, etc... with provided values.
        Can handle multiple params at once using kwargs
        :param kwargs: keyword arguments such as mag=5, dur=10,...
        """
        for key, value in kwargs.items():
            # Update effect params with provided data
            if hasattr(self, key):
                if not has_mag(self.name) and key == "mag":
                    # Do not allow mag update if effect doesn't have magnitude
                    pass
                setattr(self, key, value)
        # Recalculate new effect cost
        self.is_target = True if self.range == "Target" else False
        self.eff_cost = self._calc_eff_cost()

    def update(self, eff):
        for attr, value in vars(eff).items():
            setattr(self, attr, value)


class Spell:
    """
    Class that stores a list of effects and generates info about the entire spell
    """
    def __init__(self, *effs):
        self.effects = []
        self.effects.extend(effs)
        self._calc_derived_fields()

    def __str__(self):
        summary = (f"School: {self.dominant_school}\n"
                   f"Required Skill Level: {self.skill_required}\n"
                   f"Unmodified Cost: {self.total_cost}\n")
        effects = ("Effects:\n" +
                   "".join(["\t- " + str(eff) + "\n" for eff in self.effects]))
        return summary + effects

    def _calc_derived_fields(self):
        self.dominant_school = self._determine_school()
        self.total_cost = self._calc_cost()
        self.skill_required = self._determine_skill_req()

    def _determine_school(self):
        """
        The spell's school is the school of its highest magnitude effect
        """
        greatest = [def_string, def_int]
        for eff in self.effects:
            if eff.eff_cost > greatest[1]:
                greatest = [eff.school, eff.eff_cost]
        return greatest[0]

    def _calc_cost(self):
        """
        The spell's cost is the sum of its effects' costs
        """
        return def_int + sum([eff.eff_cost for eff in self.effects])

    def _determine_skill_req(self):
        """
        The skill level requirement is determined from the base Magicka
        cost of the overall spell (summing the costs of all individual
        effects, and without adjusting based on your current skill level):
            Magicka < 26: no skill level requirement
            26 ≤ Magicka < 63: requires skill of 25
            63 ≤ Magicka < 150: requires skill of 50
            150 ≤ Magicka < 400: requires skill of 75
            Magicka ≥ 400: requires skill of 100
        """
        for skill, threshold in skill_reqs.items():
            if self.total_cost < threshold:
                return skill
        else:
            return None

    def _match_eff(self, eff: [str, Effect], str_detail=def_string):
        """
        Determine if an effect (including sub-effect if applicable) already
        exists in a spell.

        :param eff: the effect or name of effect to search for
        :param str_detail: only needed in the case eff is a str and effect has details
        :return: int index of found effect or None if not found
        """
        # Extract info from effect param
        eff_name = eff if isinstance(eff, str) else eff.name
        eff_det = str_detail if isinstance(eff, str) else eff.details
        # Check if effect is already on spell
        for idx, ee in enumerate(self.effects):
            # In the case of skill/attribute effects
            if eff_name == ee.name and has_details(eff_name):
                # Input validation
                if eff_det == def_string:
                    raise AttributeError(f"Details not provided for {eff_name}")
                # Check the effect details
                if eff_det == ee.details:
                    return idx
            # In the case of other effects without sub-effects
            elif eff_name == ee.name:
                return idx
        # If not found, return none
        return None

    def add_effect(self, eff: Effect):
        # Effect text for logging
        eff_text = eff.name + (f": {eff.details}" if has_details(eff.name) else "")
        # Check if effect is already on spell
        exst_eff_idx = self._match_eff(eff)
        if exst_eff_idx is not None:
            # Update existing effect
            self.effects[exst_eff_idx].update(eff)
            logger.info(f"Updated {eff_text}")
        else:
            # Effect didn't already exist
            self.effects.append(eff)
            logger.info(f"Added {eff_text}")
        # Recalculate derived fields
        self._calc_derived_fields()
        return True

    def update_effect_from_str(self, eff_name: str, **kwargs):
        # Get details if exist
        str_detail = kwargs.get("details", def_string)
        # Effect text for logging
        eff_text = eff_name + (f": {str_detail}" if has_details(eff_name) else "")
        # Check if effect is already on spell
        exst_eff_idx = self._match_eff(eff_name, str_detail)
        if exst_eff_idx is None:
            logger.warning(f"Effect [{eff_text}] not present in spell.")
            return False
        # Effect exists in spell
        # Update existing effect with new params
        self.effects[exst_eff_idx].set_param(**kwargs)
        # Recalculate derived fields
        self._calc_derived_fields()
        return True

    def remove_effect(self, eff_name: str, str_detail=def_string):
        # Effect text for logging
        eff_text = eff_name + (f": {str_detail}" if has_details(eff_name) else "")
        # Check if effect is already on spell
        exst_eff_idx = self._match_eff(eff_name, str_detail)
        if exst_eff_idx is None:
            logger.warning(f"Effect [{eff_text}] not present in spell.")
            return False

        # Effect exists in spell
        self.effects.pop(exst_eff_idx)
        self._calc_derived_fields()
        logger.info(f"Removed {eff_text}")
        return True


class SpellMaker:
    """
    This class
    """

    def __init__(self, skills: dict = {}):
        # The DataFrame object containing the Excel sheet data
        self.df = pd.read_excel(fp)
        # The working custom spell object
        self.current_spell = None
        # Info for determining spell casting cost
        self.skills = skills
        self.casting_cost = self._calc_cost()

    def _calc_cost(self):
        """
        The spell's casting cost is the sum of its effects' costs
        """
        if not self.current_spell:
            return 0
        # Get school and cost for each component effect
        print(self.current_spell)
        spell_components = [{eff.school:eff.eff_cost} for eff in self.current_spell.effects]
        # Verify all needed casting skills are known
        used_schools = set([list(sc.keys())[0] for sc in spell_components])
        skill_not_found = True if True in [s not in self.skills.keys() for s in used_schools] else False
        if skill_not_found:
            logger.warning("Cannot calculate casting cost, please add magic skills")
            return 0
        # Calculate skill-modified effect costs
        casting_cost = 0
        for eff in spell_components:
            for k, v in eff.items():
                # casting cost multiplier = 1.4 - 0.012 × Skill
                v *= 1.4 - 0.012 * min(self.skills.get(k), 100)  # max discount 100
                casting_cost += v
        return round(casting_cost, 2)

    def update_skills(self, skill_dict: dict):
        """
        Update the saved skill values with the provided dict
        """
        valid_skills = ["Alteration", "Conjuration", "Destruction",
                        "Illusion", "Mysticism", "Restoration"]
        # Input validation
        new_skills = {}
        for k, v in skill_dict.items():
            if k in valid_skills:
                new_skills[k] = v
        # Update the valid skills
        self.skills.update(new_skills)

    def _get_eff(self, name: str, **kwargs):
        """
        Get the info from the data table for a specified effect
        """
        eff_data = self.df[sslc(self.df["Effect Name"]) == sslc(name)].squeeze()
        effect = Effect(data=eff_data, **kwargs)
        return effect

    def update_spell(self, eff: [str, Effect], **kwargs):
        if not self.current_spell:
            # No existing spell
            if isinstance(eff, str):
                # Get effect obj from str + kwargs
                effect = self._get_eff(eff, **kwargs)
            else:
                effect = eff
            self.current_spell = Spell(effect)
        else:
            # Existing Spell
            if isinstance(eff, str):
                # Determine whether effect is already present
                str_detail = kwargs.get("details", def_string)
                existing_idx = self.current_spell._match_eff(eff, str_detail)
                if existing_idx is not None:
                    self.current_spell.update_effect_from_str(eff, **kwargs)
                else:
                    effect = self._get_eff(eff, **kwargs)
                    self.current_spell.add_effect(effect)
            else:
                self.current_spell.add_effect(eff)
        self.casting_cost = self._calc_cost()
