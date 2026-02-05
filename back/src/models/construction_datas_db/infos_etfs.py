import yfinance as yf
import pandas as pd
import os


tickers_etf = [
    "0CAC.PA","0EMU.PA","0SWE.PA","0USE.PA","100H.PA","26ID.PA","26TP.PA","27IT-EUR.PA","28ID.PA","28IY.PA",
    "29GI.PA","29ID-EUR.PA","29IT-EUR.PA","30ID-EUR.PA","30IG.PA","500.PA","500H.PA","500U.PA","50E.PA","5OGE.PA",
    "5OGU.PA","8G19V.PA","AABAB.PA","AABCH.PA","AABDX.PA","AABEN.PA","AABFB.PA","AABGB.PA","AABKX.PA","AADA.PA",
    "AAFIN.PA","AAHLT.PA","AAIND.PA","AAINS.PA","AARB-EUR.PA","AARTL.PA","AASI.PA","AASTX.PA","AASU.PA","AATCX.PA",
    "AATLC.PA","AAUTL.PA","AAVE-EUR.PA","ABCH-EUR.PA","ABDJE.PA","ABDJI.PA","ABHSN.PA","ABIU.PA","ABKSP.PA","ABNSP.PA",
    "ABNSQ.PA","ABSMI.PA","ABTC.PA","ACE27.PA","ACE29.PA","ACE32.PA","ACES.PA","ACESD.PA","ACLU.PA","ACWE.PA",
    "ACWI.PA","ADAVE.PA","ADAW.PA","ADOT-EUR.PA","AEEM.PA","AEJ.PA","AEME.PA","AEMUS.PA","AETH.PA","AEUSE.PA",
    "AFLE.PA","AFLT.PA","AFRHG.PA","AFRHU.PA","AFRN.PA","AGEB.PA","AGES.PA","AGESD.PA","AHYE.PA","AHYU.PA",
    "AIAA-EUR.PA","AIMX-EUR.PA","AINF-EUR.PA","AINJ-EUR.PA","AIPE.PA","AIPU.PA","AJASE.PA","AJASH.PA","AJASR.PA","ALAT.PA",
    "ALAU.PA","ALGO.PA","ALINK.PA","ALTC-EUR.PA","ALTS-EUR.PA","AM3A.PA","AMINA.PA","ANRJ.PA","ANX.PA","ANXU.PA",
    
    "AOPT-EUR.PA","APTOS.PA","APX.PA","ARMY.PA","ASI.PA","ASOL-EUR.PA","ASTX-EUR.PA","ASUI-EUR.PA","ATIA.PA","AUEM.PA",
    "AUNI-EUR.PA","AUSSD.PA","AUSSE.PA","AUSSH.PA","AUSSR.PA","AVAX-EUR.PA","AWAT.PA","AWDSE.PA","AWDSH.PA","AWDSR.PA",
    "AXLM-EUR.PA","AXRP-EUR.PA","AXTZ-EUR.PA","B26A.PA","B28A.PA","BIODV.PA","BITC.PA","BLOC.PA","BLUE.PA","BLUSD.PA",
    "BMAC.PA","BNBA-EUR.PA","BNK.PA","BNKE.PA","BOLD-EUR.PA","BRES.PA","BSRIC.PA","BSRID.PA","BSX.PA","BTC.PA",
    "BTC0E.PA","BTC1.PA","BTCE.PA","BTCG-EUR.PA","BTPS.PA","BUYB.PA","BX4.PA","BXX.PA","BYBE.PA","BYBU.PA",
    "C1U.PA","C3M.PA","C40.PA","C4D.PA","C50.PA","C50U.PA","C53D.PA","C5E.PA","C6E.PA","CA40.PA",
    "CAC.PA","CACC.PA","CAPE.PA","CAPH.PA","CAPU.PA","CASHE.PA","CB3.PA","CBTC-EUR.PA","CC1.PA","CC1U.PA",
    "CC4.PA","CD5.PA","CD8.PA","CD9.PA","CE8.PA","CEC.PA","CEM.PA","CETH.PA","CEU.PA","CEU2.PA",
    "CF1.PA","CG1.PA","CG9.PA","CHINE.PA","CHINU.PA","CHIP.PA","CHM.PA","CI2.PA","CI2U.PA","CITY-EUR.PA",
    "CJ1.PA","CL2.PA","CLEM.PA","CLIM.PA","CLMA.PA","CLOR.PA","CLWD.PA","CM5E.PA","CM9.PA","CMSE.PA",
    
    "CMU.PA","CMUD.PA","CN1.PA","CNAA.PA","CNB.PA","CNEG.PA","CNY.PA","CODW.PA","COMO.PA","COSE.PA",
    "COSW.PA","CP9.PA","CP9U.PA","CRON.PA","CRP.PA","CS1.PA","CS9.PA","CSH.PA","CSH2.PA","CSW.PA",
    "CSWC.PA","CU2.PA","CU2U.PA","CU9.PA","CV9.PA","CW8.PA","CW8U.PA","CWE.PA","CWEU.PA","CYEA.PA",
    "DA20.PA","DAPP.PA","DAX.PA","DBMF.PA","DBMFE.PA","DCAM.PA","DEFS.PA","DFND.PA","DFNS.PA","DGGE.PA",
    "DGRA.PA","DI27.PA","DI35-EUR.PA","DIVA.PA","DJE.PA","DOTVE-XPAR.PA","DOTW.PA","DSB.PA","DSD.PA","DSP5.PA",
    "E40.PA","EAGG.PA","EBBB.PA","EBBU.PA","EBUY.PA","ECN.PA","ECND.PA","ECR1.PA","ECRP.PA","ECRP3.PA",
    "EDEU.PA","EDIV.PA","EEA.PA","EEE.PA","EEI.PA","EEMK.PA","EEMU.PA","EESG.PA","EESM.PA","EEUE.PA",
    "EGOV.PA","EGRA.PA","EGRI.PA","EGRO.PA","EISR.PA","EJAH.PA","EJAP.PA","EJAPU.PA","EKLD.PA","EKLDC.PA",
    "EKUS.PA","ELCR.PA","ELLE.PA","ELTC-EUR.PA","EMBH.PA","EMBI.PA","EMEH.PA","EMERG.PA","EMGA.PA","EMHD.PA",
    "EMIS.PA","EMLC.PA","EMLD.PA","EMQQ.PA","EMRG.PA","EMSR.PA","EMSRI.PA","EMWD.PA","EMWE.PA","EMXC.PA",
    
    "EMXU.PA", "ENAM.PA", "ENG.PA", "ENGUS.PA", "ENRG.PA", "EPAB.PA", "EPEA.PA", "EPEJ.PA", "EPRA.PA", "EPRE.PA",
    "EQQQ.PA", "EQUA.PA", "ERO.PA", "ERTH.PA", "ESD.PA", "ESDD.PA", "ESE.PA", "ESEH.PA", "ESGE.PA", "ESGH.PA",
    "ESGO.PA", "ESPO.PA", "ETBB.PA", "ETDD.PA", "ETH0E.PA", "ETHC-EUR.PA", "ETZ.PA", "ETZD.PA", "EUCO.PA", "EUDIV.PA",
    "EUDV.PA", "EUHD.PA", "EUSC.PA", "EUSRI.PA", "EVAE.PA", "EVOE.PA", "EWLD.PA", "EWRD.PA", "EWSP-EUR.PA", "EXCN.PA",
    "FAITH.PA", "FGBL.PA", "FINSW.PA", "FLQA.PA", "FLXT.PA", "FM26.PA", "FM27.PA", "FM28.PA", "FM29.PA", "FM30.PA",
    "FMI.PA", "FOFD.PA", "FOHW.PA", "FOO.PA", "FPXU.PA", "FRCP.PA", "FREP.PA", "FTSE.PA", "FUJI.PA", "FUTR-EUR.PA",
    "GAGG.PA", "GAGH.PA", "GAHU.PA", "GASR.PA", "GDIG.PA", "GDX.PA", "GDXJ.PA", "GE110.PA", "GE710.PA", "GEMU.PA",
    "GEU3C.PA", "GEU3D.PA", "GEU7C.PA", "GFA.PA", "GGOV.PA", "GGRA.PA", "GGRI.PA", "GILI.PA", "GILS.PA", "GLDM.PA",
    "GLFI.PA", "GLHL.PA", "GLIT.PA", "GLUX.PA", "GOAI.PA", "GOAT.PA", "GOD10.PA", "GOV10.PA", "GOVH.PA", "GOVS.PA",
    "GR8.PA", "GRCTB.PA", "GRE.PA", "GREAD.PA", "GREAL.PA", "GSCU.PA", "GSSBD.PA", "GUARD.PA", "GWT.PA", "HAMO-EUR.PA",

    "HASH.PA", "HCAN.PA", "HCAS.PA", "HDLV.PA", "HEMA.PA", "HEU.PA", "HHH.PA", "HIES.PA", "HIJS.PA", "HIPS.PA",
    "HIUS.PA", "HIWS.PA", "HLT.PA", "HLTW.PA", "HMES.PA", "HMJS.PA", "HODL.PA", "HODLV.PA", "HODLX.PA", "HSJA.PA",
    "HSRID.PA", "HSTE.PA", "HSUK.PA", "HWSS.PA", "HYBB.PA", "HYCC.PA", "HYDRO.PA", "HYDUS.PA", "HYEM.PA", "HYFA.PA",
    "HYSRI.PA", "IART.PA", "IB25.PA", "IB27.PA", "IBE5.PA", "IBE7.PA", "ID25.PA", "IG35.PA", "IMIE.PA", "IND.PA",
    "INDEP.PA", "INDO.PA", "INDW.PA", "INFL.PA", "INFU.PA", "INR.PA", "INRE.PA", "INS.PA", "IQEC.PA", "IQEE.PA",
    "IQJP.PA", "ISCH.PA", "ISJH.PA", "ISRA.PA", "ISRC.PA", "ISRD.PA", "ISRG.PA", "ISRJ.PA", "ISRM.PA", "ISRU.PA",
    "ISUH.PA", "ITEK.PA", "IU28-EUR.PA", "IU29-EUR.PA", "IWDS-EUR.PA", "IX28-XPAR.PA", "IX29-XPAR.PA", "JAPAN.PA", "JBEM.PA", "JEDI.PA",
    "JNKA.PA", "JNKE.PA", "JPHC.PA", "JPHD.PA", "JPHE.PA", "JPHG.PA", "JPHU.PA", "JPJY.PA", "JPN.PA", "JPNH.PA",
    "JPNK.PA", "JPNY.PA", "JPX4.PA", "JPXH.PA", "KRW.PA", "L100.PA", "LC30.PA", "LC33.PA", "LC36.PA", "LC39.PA",
    "LCCN.PA", "LCEUD.PA", "LCWLD.PA", "LEM.PA", "LIDO.PA", "LQQ.PA", "LUXU.PA", "LVC.PA", "LVD.PA", "LVE.PA",
    
    "LWCE.PA", "LWCR.PA", "LWLD.PA", "MA13.PA", "MA35.PA", "MAA.PA", "MATW.PA", "MCEU.PA", "MEH.PA", "METE.PA",
    "MEU.PA", "MEUD.PA", "MEUR.PA", "MFE.PA", "MFEC.PA", "MFED.PA", "MGT.PA", "MIB.PA", "MILL.PA", "MIVU.PA",
    "MJP.PA", "MLUX.PA", "MMS.PA", "MOAT.PA", "MOTU.PA", "MSE.PA", "MSES.PA", "MTA.PA", "MTB.PA", "MTC.PA",
    "MTD.PA", "MTE.PA", "MTF.PA", "MTH.PA", "MTI.PA", "MTPI.PA", "MUS.PA", "MUSA.PA", "MUSRI.PA", "MWO.PA",
    "MWOQ.PA", "MWOS.PA", "MWRD.PA", "NATO.PA", "NCLR.PA", "NDXH.PA", "NEAR-EUR.PA", "NRAM.PA", "NRGW.PA", "NRJ.PA",
    "NRJC.PA", "NTSG.PA", "NTSZ-XPAR.PA", "NUCL.PA", "OBBA.PA", "OBGE.PA", "OBLI.PA", "OBUS.PA", "OFIEU.PA", "OFIUS.PA",
    "OIHV.PA", "ONDO-EUR.PA", "OP4E.PA", "OP5E.PA", "OP5H.PA", "OP6E.PA", "OP7E.PA", "OP7H.PA", "OP8E.PA", "OP9E.PA",
    "P500H.PA", "PAACE.PA", "PAACU.PA", "PAASI.PA", "PABH.PA", "PABU.PA", "PABW.PA", "PABZ.PA", "PAEEM.PA", "PAEJ.PA",
    "PALAT.PA", "PANX.PA", "PASI.PA", "PCEU.PA", "PDJE.PA", "PE500.PA", "PEF.PA", "PEH.PA", "PEMS.PA", "PEU.PA",
    "PFT.PA", "PINR.PA", "PLAN.PA", "PLEM.PA", "PMEH.PA", "PNAS.PA", "POLY.PA", "PQVM.PA", "PRAC.PA", "PRAJ.PA",
    
    "PSP5.PA", "PSPH.PA", "PSPS.PA", "PSRW.PA", "PTPXE.PA", "PTPXH.PA", "PUST.PA", "PYTH-EUR.PA", "QCEU.PA", "QEIG.PA",
    "QEUR.PA", "QGLOE.PA", "QNXT-EUR.PA", "QTOP-EUR.PA", "QUED.PA", "QUSAE.PA", "R2US.PA", "REMX.PA", "REUSD.PA", "REUSE.PA",
    "RIO.PA", "RNDR-EUR.PA", "RS2K.PA", "RS2U.PA", "S500.PA", "S500H.PA", "S6EW.PA", "SADU.PA", "SAUDI.PA", "SBTCU-EUR.PA",
    "SCITY-EUR.PA", "SDOT.PA", "SEL.PA", "SEME.PA", "SETH-EUR.PA", "SGQI.PA", "SHC.PA", "SHTE.PA", "SMC.PA", "SMH.PA",
    "SMOT.PA", "SOLVE-XPAR.PA", "SP20-EUR.PA", "SP5.PA", "SP5C.PA", "SP5H.PA", "SPEA.PA", "SPEEU.PA", "SPEUH.PA", "SPEUS.PA",
    "SPHC.PA", "SPTRE.PA", "SPTRH.PA", "SPY4.PA", "SPY5.PA", "SRI3C.PA", "SRIC.PA", "SRIC3.PA", "SRIC5.PA", "SRIC6.PA",
    "SRIC7.PA", "SRICD.PA", "SRID7.PA", "SRIE.PA", "SRIEC.PA", "SRIJ.PA", "SRIJC.PA", "SRIUC.PA", "SRIUD.PA", "STK.PA",
    "STN.PA", "STP.PA", "STPU.PA", "STQ.PA", "STR.PA", "STS.PA", "STT.PA", "STU.PA", "STW.PA", "STZ.PA",
    "TDIV-XPAR.PA", "TELE.PA", "TELW.PA", "TI25.PA", "TIAB.PA", "TNO.PA", "TNOW.PA", "TONN-EUR.PA", "TPHC.PA", "TPHG.PA",
    "TPHU.PA", "TPXE.PA", "TPXH.PA", "TPXY.PA", "TRV.PA", "TRYP.PA", "TUR.PA", "U10HK.PA", "U13HK.PA", "U710H.PA",


    "UB93V.PA", "UBBB.PA", "UCRP.PA", "UEFA.PA", "UKX.PA", "UNIC.PA", "US10.PA", "US100.PA", "US13.PA", "US37.PA",
    "US88V.PA", "US89V.PA", "USA.PA", "USAC.PA", "USAL.PA", "USAS.PA", "USCBC.PA", "USCBD.PA", "USCBH.PA", "USDIV.PA",
    "USFA.PA", "USHY.PA", "USIH.PA", "USRI-EUR.PA", "USSM.PA", "UST.PA", "USVE.PA", "UTI.PA", "VAL.PA", "VALD.PA",
    "VBTC.PA", "VDOT.PA", "VETH.PA", "VLED.PA", "VOLT.PA", "VPYT.PA", "VRTS-XPAR.PA", "VSOL.PA", "VSUI-USD.PA", "VTIA.PA",
    "VTRX.PA", "WAT.PA", "WATC.PA", "WBTC.PA", "WCBR.PA", "WCLD.PA", "WDEF.PA", "WEB3.PA", "WELL.PA", "WEMT2.PA",
    "WEMTE.PA", "WEMTH.PA", "WESE.PA", "WETFE.PA", "WEWEU.PA", "WLD.PA", "WLDH.PA", "WLSC.PA", "WORLD.PA", "WPEA.PA",
    "WPEH.PA", "WQTM.PA", "WRD.PA", "WSRI-EUR.PA", "WTAI.PA", "X13G.PA", "X1G.PA", "X1GD.PA", "XBTI.PA", "XDCN.PA",
    "XQ48V.PA", "YIEL.PA", "ZETH.PA", 'GDX', "GOLD"
]



#tickers_etf = ["500.PA", "CACC.PA"]
#print(len(set(tickers_etf)))

def infos_etfs(dossier_csv="csv", csv_bdd="csv/csv_bdd"):
    rows = []

    for i, ticker in enumerate(tickers_etf, start=1):
        print(f"[{i}/{len(tickers_etf)}] ETF : {ticker}")

        try:
            t = yf.Ticker(ticker).info

            if not t:
                print(f"  ⚠️ info vide pour {ticker}")
                continue

            rows.append(t)
            print(f"  ✅ OK ({t.get('shortName', 'NO shortName')})")

        except Exception as e:
            print(f"  ❌ ERREUR pour {ticker} → {e}")
            continue  # on passe au suivant

    if not rows:
        raise RuntimeError("❌ Aucun ETF récupéré → arrêt")

    df = pd.DataFrame(rows)

    # Colonnes sécurisées
    df["short_name_etf"] = df.get("shortName")
    df["ticker_etf_yf"] = df.get("symbol")
    df["ticker_etf"] = df["ticker_etf_yf"].apply(lambda x: x.split(".")[0] if pd.notna(x) else None)
    df["devise"] = df.get("currency")
    df["place_boursiere_etf"] = df.get("exchange")
    df["volume_moyen"] = pd.to_numeric(df.get("averageVolume"), errors="coerce") # Remplace par NaN si erreur de conversion
    df["frais_pct"] = pd.to_numeric(df.get("netExpenseRatio"), errors="coerce")

    # Gaeder seulement les colonnes utiles
    df = df[["short_name_etf", "ticker_etf_yf", "ticker_etf", "devise", "place_boursiere_etf", "volume_moyen", "frais_pct",]]
    
    # Supprime les lignes avec Short_Name_Etf vide ou NaN contrairement à df = df.dropna(subset=["Short_Name_Etf"]) que NaN seulement
    df = df[df["short_name_etf"].notna() & (df["short_name_etf"] != "")]

    # Supprime les lignes avec "USD" dans la colonne Devise car c'est des doublons d'ETF déjà présents en EUR avec moins d'encours
    df = df[df["devise"] != "USD"]

    # Forcer types numériques si champs vide(important pour SQL)
    df["volume_moyen"] = pd.to_numeric(df["volume_moyen"], errors="coerce")
    df["frais_pct"] = pd.to_numeric(df["frais_pct"], errors="coerce")
    df = df.sort_values("volume_moyen", ascending=False)
    df = df.drop_duplicates(subset="short_name_etf", keep="first")

    # Sauvegarde du fichier csv
    df.to_csv(os.path.join(csv_bdd, "etfs_infos.csv"), index=False, encoding="utf-8")

    return df


if __name__ == "__main__":
    infos_etfs("csv", "csv/csv_bdd")
    print("[✅] Les informations des etfs ont été récupérées et sauvegardées.")