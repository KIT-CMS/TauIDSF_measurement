#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts, Weight
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations, AddWeight, ReplaceWeight, Relabel
from shape_producer.process import Process
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.channel import MTTauID2018, MMTauID2018

from itertools import product

import argparse
import yaml

import logging
logger = logging.getLogger()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for 2018 Tau ID scale factor measurement.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing friend trees to data files with fake factors."
    )
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--binning", required=True, type=str, help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--gof-channel",
        default=None,
        type=str,
        help="Channel for goodness of fit shapes.")
    parser.add_argument(
        "--gof-variable",
        type=str,
        help="Variable for goodness of fit shapes.")
    parser.add_argument(
        "--num-threads",
        default=32,
        type=int,
        help="Number of threads to be used.")
    parser.add_argument(
        "--backend",
        default="classic",
        choices=["classic", "tdf"],
        type=str,
        help="Backend. Use classic or tdf.")
    parser.add_argument(
        "--tag", default="ERA_CHANNEL", type=str, help="Tag of output files.")
    parser.add_argument(
        "--skip-systematic-variations",
        default=False,
        type=str,
        help="Do not produce the systematic variations.")
    parser.add_argument(
        "-w",
        "--working-point",
        type=str,
        default="tight",
        help="Tau ID working point to be measured.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "{}_shapes.root".format(args.tag),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J_PTH_0_60, ggHEstimation_1J_PTH_60_120, ggHEstimation_1J_PTH_120_200, ggHEstimation_1J_PTH_GT200, ggHEstimation_GE2J_PTH_0_60, ggHEstimation_GE2J_PTH_60_120, ggHEstimation_GE2J_PTH_120_200, ggHEstimation_GE2J_PTH_GT200, ggHEstimation_VBFTOPO_JET3, ggHEstimation_VBFTOPO_JET3VETO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_VH2JET, qqHEstimation_PTJET1_GT200, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, FakeEstimationLT, NewFakeEstimationLT, FakeEstimationTT, NewFakeEstimationTT, DYJetsToLLEstimation, TTEstimation, VVEstimation

        from shape_producer.era import Run2018
        era = Run2018(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    wp_dict_mva = {
               "vvloose": "byVVLooseIsolationMVArun2017v2DBoldDMwLT2017_2",
               "vloose": "byVLooseIsolationMVArun2017v2DBoldDMwLT2017_2",
               "loose": "byLooseIsolationMVArun2017v2DBoldDMwLT2017_2",
               "medium": "byMediumIsolationMVArun2017v2DBoldDMwLT2017_2",
               "tight": "byTightIsolationMVArun2017v2DBoldDMwLT2017_2",
               "vtight": "byVTightIsolationMVArun2017v2DBoldDMwLT2017_2",
               "vvtight": "byVVTightIsolationMVArun2017v2DBoldDMwLT2017_2",
               "mm": "0<1",
               }
    wp_dict_deeptau = {
               "vvvloose": "byVVVLooseDeepTau2017v2p1VSjet_2",
               "vvloose": "byVVLooseDeepTau2017v2p1VSjet_2",
               "vloose": "byVLooseDeepTau2017v2p1VSjet_2",
               "loose": "byLooseDeepTau2017v2p1VSjet_2",
               "medium": "byMediumDeepTau2017v2p1VSjet_2",
               "tight": "byTightDeepTau2017v2p1VSjet_2",
               "vtight": "byVTightDeepTau2017v2p1VSjet_2",
               "vvtight": "byVVTightDeepTau2017v2p1VSjet_2",
               "mm": "0<1",
               }
    wp_dict = wp_dict_deeptau

    logger.info("Produce shapes for the %s working point of the MVA Tau ID", args.working_point)
    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = []#args.et_friend_directory
    em_friend_directory = []#args.em_friend_directory
    mt_friend_directory = []#args.mt_friend_directory
    tt_friend_directory = []#args.tt_friend_directory
    ff_friend_directory = []#args.fake_factor_friend_directory
    mt = MTTauID2018()
    mt.cuts.add(Cut(wp_dict[args.working_point]+">0.5", "tau_iso"))
    # if args.gof_channel == "mt":
    #     mt.cuts.remove("m_t")
    #     mt.cuts.remove("dZeta")
    #     mt.cuts.remove("absEta")
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, mt, friend_directory=mt_friend_directory)),
        }
    # mt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=[mt_friend_directory, ff_friend_directory]))
    #mt_fakes_for_uncs=Process("jetFakes", FakeEstimationLT(era, directory, mt, friend_directory=[mt_friend_directory, ff_friend_directory]))
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "TTL","TTT","TTJ", "VVT", "VVJ", "VVL","W"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.1))
    mt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["EMB", "ZL", "ZJ", "TTL", "TTJ", "VVJ", "VVL","W"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.1))

    # TODO: Include Z-> mumu control region.
    mm = MMTauID2018()
    mm_processes = {
        "data"  : Process("data_obs", DataEstimation       (era, directory, mm, friend_directory=[])),
        "ZLL"   : Process("ZLL",      DYJetsToLLEstimation (era, directory, mm, friend_directory=[])),
        "MMEMB" : Process("MMEMB",    ZTTEmbeddedEstimation(era, directory, mm, friend_directory=[])),
        "TT"    : Process("TT",       TTEstimation         (era, directory, mm, friend_directory=[])),
        "VV"    : Process("VV",       VVEstimation         (era, directory, mm, friend_directory=[])),
        "W"     : Process("W",        WEstimation          (era, directory, mm, friend_directory=[])),
        }
    # mm_processes["FAKES"] = None  TODO: Add fake factors or alternative fake rate estimation here
    mm_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mm,
            [mm_processes[process] for process in ["ZLL", "W", "TT", "VV"]],
            mm_processes["data"], friend_directory=[], extrapolation_factor=1.17))
    mm_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, mm,
            [mm_processes[process] for process in ["MMEMB", "W"]],
            mm_processes["data"], friend_directory=[], extrapolation_factor=1.17))



    # Variables and categories
    binning = yaml.load(open(args.binning))

    mt_categories = []
    # Goodness of fit shapes
    if args.gof_channel == "mt":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["control"]["mt"][args.gof_variable]["bins"]),
                expression=binning["control"]["mt"][args.gof_variable]["expression"])
        if "cut" in binning["control"]["mt"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["control"]["mt"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        mt_categories.append(
            Category(
                args.gof_variable,
                mt,
                cuts,
                variable=score))
    elif "mt" in args.channels:
        for cat in binning["categories"]["mt"]:
            category = Category(
                        cat,
                        mt,
                        Cuts(Cut(binning["categories"]["mt"][cat]["cut"], "category")),
                        variable=Variable(binning["categories"]["mt"][cat]["var"],
                            VariableBinning(binning["categories"]["mt"][cat]["bins"]),
                            expression=binning["categories"]["mt"][cat]["expression"]))
            mt_categories.append(category)

    # yapf: enable
    if "mt" in [args.gof_channel] + args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    mm_categories = []
    if "mm" in args.channels:
        category = Category(
                    "control",
                    mm,
                    Cuts(),
                    variable=Variable("m_vis",
                        ConstantBinning(1, 50, 150),
                        "m_vis"))
        mm_categories.append(category)

    if "mm" in args.channels:
        for process, category in product(mm_processes.values(), mm_categories):
            systematics.add(
                    Systematic(
                        category=category,
                        process=process,
                        analysis="smhtt",
                        era=era,
                        variation=Nominal(),
                        mass="125"))

    # Shapes variations

    # MC tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVL", "VVT",# "FAKES"
                            ]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVT", "VVL", "EMB",# "FAKES"
                            ]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # Jet energy scale

    # Inclusive JES shapes TODO: Check this
    jet_es_variations = []
    '''jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Run2017", "jecUnc", DifferentPipeline)'''

    # Splitted JES shapes
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to3_Run2018", "jecUncEta0to3", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to5_Run2018", "jecUncEta0to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta3to5_Run2018", "jecUncEta3to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal_Run2018", "jecUncRelativeBal",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_Run2018", "jecUncRelativeSample",
        DifferentPipeline)

    for variation in jet_es_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL",
        ]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # MET energy scale. Note: only those variations for non-resonant processes are used in the stat. inference
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn",
        DifferentPipeline)
    for variation in met_unclustered_variations:  # + met_clustered_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL",
        ]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run2018", "metRecoilResolution",
        DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run2018", "metRecoilResponse",
        DifferentPipeline)
    for variation in recoil_resolution_variations + recoil_response_variations:
        for process_nick in ["ZTT", "ZL", "ZJ", "W"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_Run2018", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process_nick in ["ZTT", "ZL", "ZJ"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight",
        SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process_nick in ["TTT", "TTL", "TTJ"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # TODO: likely not necessary, to be checked
    # jet to tau fake efficiency
    jet_to_tau_fake_variations = []
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2018", "jetToTauFake_weight",
                  Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"), "Up"))
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2018", "jetToTauFake_weight",
                  Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"), "Down"))
    for variation in jet_to_tau_fake_variations:
        for process_nick in ["ZJ", "TTJ", "W", "VVJ"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # ZL fakes energy scale
    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run2018", "tauMuFakeEsOneProng",
        DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run2018", "tauMuFakeEsOneProngPiZeros",
        DifferentPipeline)

    if "mt" in [args.gof_channel] + args.channels:
        for process_nick in ["ZL"]:
            for variation in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # lepton trigger efficiency
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in [
            "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ",
        ]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
        for process_nick in ["ZLL", "TT", "VV", "W"]:
            if "mm" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                        variation=variation,
                        process=mm_processes[process_nick],
                        channel=mm,
                        era=era)

    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
        for process_nick in ["MMEMB"]:
            if "mm" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mm_processes[process_nick],
                    channel=mm,
                    era=era)


    # b tagging
    # btag_eff_variations = create_systematic_variations(
    #     "CMS_htt_eff_b_Run2017", "btagEff", DifferentPipeline)
    # mistag_eff_variations = create_systematic_variations(
    #     "CMS_htt_mistag_b_Run2017", "btagMistag", DifferentPipeline)
    # for variation in btag_eff_variations + mistag_eff_variations:
    #     for process_nick in [
    #             "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
    #             "VVL"
    #     ]:
    #         if "et" in [args.gof_channel] + args.channels:
    #             systematics.add_systematic_variation(
    #                 variation=variation,
    #                 process=et_processes[process_nick],
    #                 channel=et,
    #                 era=era)
    #         if "mt" in [args.gof_channel] + args.channels:
    #             systematics.add_systematic_variation(
    #                 variation=variation,
    #                 process=mt_processes[process_nick],
    #                 channel=mt,
    #                 era=era)
    #         if "tt" in [args.gof_channel] + args.channels:
    #             systematics.add_systematic_variation(
    #                 variation=variation,
    #                 process=tt_processes[process_nick],
    #                 channel=tt,
    #                 era=era)
    #     for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL",  "VVL", "VVT"
    #                         ]:
    #         if "em" in [args.gof_channel] + args.channels:
    #             systematics.add_systematic_variation(
    #                 variation=variation,
    #                 process=em_processes[process_nick],
    #                 channel=em,
    #                 era=era)

    # Embedded event specifics
    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["EMB"]:#,  "FAKES"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    mt_decayMode_variations = []
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in mt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to ZTT shape to use as systematic
    tttautau_process_mt = Process(
        "TTT",
        TTTEstimation(
            era, directory, mt, friend_directory=[]))
    if "mt" in [args.gof_channel] + args.channels:
        for category in mt_categories:
            mt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Down"),
                    mass="125"))

            mt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Up"),
                    mass="125"))

    # jetfakes
    # fake_factor_variations_mt = []
    # for systematic_shift in [
    #         "ff_qcd{ch}_syst_Run2017{shift}",
    #         "ff_qcd_dm0_njet0{ch}_stat_Run2017{shift}",
    #         "ff_qcd_dm0_njet1{ch}_stat_Run2017{shift}",
    #         #"ff_qcd_dm1_njet0{ch}_stat_Run2017{shift}",
    #         #"ff_qcd_dm1_njet1{ch}_stat_Run2017{shift}",
    #         "ff_w_syst_Run2017{shift}",
    #         "ff_w_dm0_njet0{ch}_stat_Run2017{shift}",
    #         "ff_w_dm0_njet1{ch}_stat_Run2017{shift}",
    #         #"ff_w_dm1_njet0{ch}_stat_Run2017{shift}",
    #         #"ff_w_dm1_njet1{ch}_stat_Run2017{shift}",
    #         "ff_tt_syst_Run2017{shift}",
    #         "ff_tt_dm0_njet0_stat_Run2017{shift}",
    #         "ff_tt_dm0_njet1_stat_Run2017{shift}",
    #         #"ff_tt_dm1_njet0_stat_Run2017{shift}",
    #         #"ff_tt_dm1_njet1_stat_Run2017{shift}"
    # ]:
    #     for shift_direction in ["Up", "Down"]:
    #         fake_factor_variations_mt.append(
    #             ReplaceWeight(
    #                 "CMS_%s" % (systematic_shift.format(ch='_mt', shift="").replace("_dm0", "")),
    #                 "fake_factor",
    #                 Weight(
    #                     "ff2_{syst}".format(
    #                         syst=systematic_shift.format(
    #                             ch="", shift="_%s" % shift_direction.lower())
    #                         .replace("_Run2017", "")),
    #                     "fake_factor"), shift_direction))
    # if "mt" in [args.gof_channel] + args.channels:
    #     for variation in fake_factor_variations_mt:
    #         systematics.add_systematic_variation(
    #             variation=variation,
    #             process=mt_processes["FAKES"],
    #             channel=mt,
    #             era=era)
    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.DEBUG)
    main(args)
