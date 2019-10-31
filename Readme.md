# TAUID Measurement

Properties of the analysis: 
## Selection

### Muon

* pt_1:
    * 2016: pt_1 > 23 GeV
    * 2017: pt_1 > 25 GeV || > 28 GeV
    * 2018: pt_1 > 25 GeV
* eta_1 < 2.4
* trg_singlemuon_24:
    * 2016: (HLT_IsoMu22 || IsoTkMu22)
    * 2017: (HLT_IsoMu24 || HLT_IsoMu27)
    * 2018: (HLT_IsoMu24)
* iso_1 < 0.15
* medium ID
* dxy_1 < 0.045
* dz < 0.2

### Tau

* pt > 20 GeV
* eta < 2.3
* againstMuonTight3_2 (tight antimuon)
* againstElectronVLooseMVA6_2 (vvloose antielectron)
* dz < 0.2

### Event

* opposite Sign
* extraelec_veto
* extramuon_veto
* dilepton_veto
* mT_1 < 60 GeV
* abs(eta_1 - eta_2 ) < 1.5 
* pZetaMissVis > -25 GeV
* flagMETFilter

## Corrections

* Muon ID SF
* Muon ISO SF
* Z_PT reweighting
* Top pt reweighting
* (generatorWeights)
* PileUp
* recoil Corrections
* lepton->tau fake 


## Samples

* DYJets all
* EMB
* TT
* ST
* WJets all
* WW
* WZ
* ZZ
* SingleMuon

### JetFakeEstimation

1. Use Z->µµ + Jets Events
2. Selection: 
   1. Muon: pt_1 see base selection for each year, pt_2 > 15 GeV
   2. Tau see base selection
   3. Z Mass Window:  70 < mZ < 110,
3. Fake rate Tight / (VLoose && !Tight), per decay mode

### Z->µµ Control Region

Same selection as for JetFakes ?

## Uncertainty model

uncorrelated across years

### Correlated with Z->µµ Region

* muon id/iso/trigger - 2%
* Lumi - 2.5%
* DY xsec - 2%
* QCD norm - 30%
* vv xsec 6 %
* ttbar xsec 5.5 %
* st xsec 5.5 %
  
### Uncorrelated with Z->µµ

* W norm 5%
* jet->tau 10 %
* µ->tau 50 % (100 % for 2018)
* TauEnergyScale 3%
* Jet->TauEnergyScale 10%
* Muon->tauEnergyScale 3%
* bin by bins

## Fit

The Tau ID SF is measured by fitting the ZTT MC yield to data. It is measured binned in the inclusively or binned in the pT or the reconstructed decay mode of the tau lepton. The binning of the measurement is as follows:

* pt: [20,25,30,35,40,50,70,200]
* dm(MVA): [0,1,10]
* dm(DeepTau): [0,1,10,11]

To run the measurement invoke
```shell
bash TauIDSF_measurement/measure_TauIDSF.sh $ERA mt
```
from the top level directory of the [sm-htt-analysis](https://github.com/KIT-CMS/sm-htt-analysis) repository. This produces the necessary shapes for the inclusive and binned measurements and creates the datacards, workspace and performs the fit for the inclusive or one of the binned measurements specified inside the file. Additionally it produces prefit and postfit shapes and creates plots of these shapes.

# Producing the shapes

ToDo

# Creating the datacard

ToDo

# Creating the workspace

ToDo

# Performing the fit

ToDo

# Prefit and postfit shapes

ToDo

# Plotting

ToDo
