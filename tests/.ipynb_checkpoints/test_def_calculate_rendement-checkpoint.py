from src.models.control_datas.connexion_db_datas import calculate_rendement
import pandas as pd

def test_calculate_rendement():
    # Simuler les données
    df = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=6, freq="M"),
        "Close": [100, 110, 120, 130, 140, 150]
    })

    result = calculate_rendement(df, [3, 6])

    assert result["3 mois"] == "11.11"
    assert result["6 mois"] == "50.00"

def test_calculate_rendement_periode_vide():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2023-01-01"]),
        "Close": [100]
    })

    result = calculate_rendement(df, [6])
    assert result["6 mois"] is None

def test_calculate_rendement_aucune_donnee():
    df = pd.DataFrame(columns=["Date", "Close"])
    result = calculate_rendement(df, [6])
    assert result["6 mois"] is None