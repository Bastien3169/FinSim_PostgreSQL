from models.control_datas.connexion_db_datas import calculate_rendement
import pandas as pd

# Ici, le test va se passer sans "fail"
def test_calculate_rendement_nominal():
    df = pd.DataFrame({"Date": pd.date_range(start="2024-01-01", periods=6, freq="M"),"Close": [100, 110, 120, 130, 140, 150]})
    # On demande les rendements à 3 et 6 mois
    result = calculate_rendement(df, [3, 6])
    # 3 mois : Juin(150) / Mars(120) - 1 = 25.00%
    assert result["3 mois"] == "25.00"


# Ici, le test va être "Fail" car le rendement sera faux et il y aura un "FutureWarning" car "dateutil" déprécié dans Pandas
def test_calculate_rendement_faux():
    df = pd.DataFrame({"Date": pd.date_range(start="2024-01-01", periods=2, freq="M"),"Close": [110, 120]})
    result = calculate_rendement(df, [1])
    assert result == {"1 mois": "11.23"}  # faux exprès : 9.09 ≠ 11.23


