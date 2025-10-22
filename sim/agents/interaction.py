import math

def preference_to_interact(
    E_self, A_self, N_self,
    E_partner, A_partner, N_partner,
    familiarity, attractiveness,
    same_gender=True, bad_weather=False
):
    """
    Estimate preference to interact based on Weiß et al. (2023).
    Inputs: 1–7 Likert ratings for traits, familiarity, attractiveness.
    Output: predicted preference score (1–7).
    """

    # --- Base partner effects ---
    score = 0
    score += 0.103 * E_partner
    score += 0.164 * A_partner
    score -= 0.060 * N_partner

    # --- Self effects ---
    score += 0.019 * A_self
    score -= 0.001 * N_self

    # --- Interactions ---
    score += 0.002 * (E_self * E_partner)
    score += 0.004 * (A_self * N_partner)

    # --- Covariates ---
    score += 0.226 * familiarity
    score += 0.097 * attractiveness
    if same_gender:
        score += 0.158
    if bad_weather:
        score -= 0.05  # small penalty, nonsignificant in paper

    # --- Exploratory: trait distance penalty ---
    trait_distance = math.sqrt(
        (E_self - E_partner)**2 +
        (A_self - A_partner)**2 +
        (N_self - N_partner)**2
    )
    score -= 0.162 * trait_distance

    # --- Normalize to 1–7 scale ---
    score = max(1, min(7, score))

    return round(score, 2)


# Example usage
print(preference_to_interact(
    E_self=6, A_self=5, N_self=2,
    E_partner=6, A_partner=6, N_partner=3,
    familiarity=5, attractiveness=4,
    same_gender=True, bad_weather=False))