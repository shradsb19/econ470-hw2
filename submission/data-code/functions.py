import pandas as pd


MA_PATH = "/home/sbandl2/econ470/a0/work/ma-data/ma"


def read_contract(path):
    col_names = [
        "contractid", "planid", "org_type", "plan_type", "partd", "snp", "eghp",
        "org_name", "org_marketing_name", "plan_name", "parent_org", "contract_date"
    ]

    df = pd.read_csv(
        path,
        skiprows=1,
        names=col_names,
        encoding="latin1"
    )

    return df


def read_enroll(path):
    col_names = [
        "contractid", "planid", "ssa", "fips", "state", "county", "enrollment"
    ]

    df = pd.read_csv(
        path,
        skiprows=1,
        names=col_names,
        na_values="*"
    )

    return df


def load_month(month, year):
    contract_path = f"{MA_PATH}/enrollment/Extracted Data/CPSC_Contract_Info_{year}_{month}.csv"
    enroll_path = f"{MA_PATH}/enrollment/Extracted Data/CPSC_Enrollment_Info_{year}_{month}.csv"

    contract_info = read_contract(contract_path)
    enroll_info = read_enroll(enroll_path)

    contract_info["planid"] = pd.to_numeric(contract_info["planid"], errors="coerce")
    enroll_info["planid"] = pd.to_numeric(enroll_info["planid"], errors="coerce")

    merged = pd.merge(
        enroll_info,
        contract_info,
        on=["contractid", "planid"],
        how="left"
    )

    merged["month"] = int(month)
    merged["year"] = year

    return merged


def read_service_area(path):
    col_names = [
        "contractid", "org_name", "org_type", "plan_type", "partial", "eghp",
        "ssa", "fips", "county", "state", "notes"
    ]

    df = pd.read_csv(
        path,
        skiprows=1,
        names=col_names,
        encoding="latin1",
        engine="python",
        on_bad_lines="skip"
    )

    return df


def load_month_sa(month, year):
    path = f"{MA_PATH}/service-area/Extracted Data/MA_Cnty_SA_{year}_{month}.csv"

    df = read_service_area(path)
    df["month"] = int(month)
    df["year"] = year

    return df


def read_penetration(path):
    col_names = [
        "state", "county", "fips_state", "fips_county", "fips",
        "ssa_state", "ssa_county", "ssa", "eligibles", "enrolled", "penetration"
    ]

    df = pd.read_csv(
        path,
        skiprows=1,
        names=col_names,
        na_values=["", "NA", "*", "-", "--"]
    )

    df["eligibles"] = (
        df["eligibles"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df["enrolled"] = (
        df["enrolled"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df["penetration"] = (
        df["penetration"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df["eligibles"] = pd.to_numeric(df["eligibles"], errors="coerce")
    df["enrolled"] = pd.to_numeric(df["enrolled"], errors="coerce")
    df["penetration"] = pd.to_numeric(df["penetration"], errors="coerce")

    return df


def load_month_pen(month, year):
    path = f"{MA_PATH}/penetration/Extracted Data/State_County_Penetration_MA_{year}_{month}.csv"

    df = read_penetration(path)
    df["month"] = int(month)
    df["year"] = year

    return df


def mapd_clean_merge(ma_data, mapd_data, year):
    ma_data = ma_data[["contractid", "planid", "state", "county", "premium"]].copy()
    ma_data = ma_data.drop_duplicates()

    mapd_data = mapd_data[
        [
            "contractid", "planid", "state", "county",
            "premium_partc", "premium_partd_basic",
            "premium_partd_supp", "premium_partd_total",
            "partd_deductible"
        ]
    ].copy()

    mapd_data["planid"] = pd.to_numeric(mapd_data["planid"], errors="coerce")
    mapd_data = mapd_data.drop_duplicates()

    merged = pd.merge(
        ma_data,
        mapd_data,
        on=["contractid", "planid", "state", "county"],
        how="outer"
    )

    merged["year"] = year

    return merged
