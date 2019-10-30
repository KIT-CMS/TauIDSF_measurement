#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles

import argparse
import copy
import yaml

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis")
    parser.add_argument(
        "-c",
        "--channels",
        nargs="+",
        type=str,
        required=True,
        help="Channels")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--gof-variable",
        type=str,
        default=None,
        help="Enable plotting goodness of fit shapes for given variable")
    parser.add_argument(
        "--png", action="store_true", help="Save plots in png format")
    parser.add_argument(
        "--categories",
        type=str,
        required=True,
        help="Select categorization.")
    parser.add_argument(
        "--bin",
        type=str,
        required=True,
        help="Select bin to be drawn.")
    parser.add_argument(
        "--normalize-by-bin-width",
        action="store_true",
        help="Normelize plots by bin width")
    parser.add_argument(
        "--fake-factor",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--chi2test",
        action="store_true",
        help="Print chi2/ndf result in upper-right of subplot")

    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main(args):
    if args.gof_variable != None:
        channel_categories = {
            "et": ["100"],
            "mt": ["100"],
            "tt": ["100"],
            "em": ["100"],
            "mm": ["100"],
        }
    channel_categories = {
            "mt": [args.bin],
            "mm": ["100"],
    }
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    if args.gof_variable != None:
        category_dict = {"100": "inclusive"}
    elif args.categories == "inclusive":
        category_dict = {
            "1": "inclusive",
            "100": "cr",
        }
    elif args.categories == "pt_binned":
        category_dict = {
            "1": "[20,25]",
            "2": "[25,30]",
            "3": "[30,35]",
            "4": "[35,40]",
            "5": "[40,50]",
            "6": "[50,70]",
            "7": "[70,]",
            "100": "cr",
        }
    elif args.categories == "ptdm_binned":
        category_dict = {
             "1": "[20,25], DM0",
             "2": "[20,25], DM1",
             "3": "[20,25], DM10",
             "4": "[25,30], DM0",
             "5": "[25,30], DM1",
             "6": "[25,30], DM10",
             "7": "[30,35], DM0",
             "8": "[30,35], DM1",
             "9": "[30,35], DM10",
            "10": "[35,40], DM0",
            "11": "[35,40], DM1",
            "12": "[35,40], DM10",
            "13": "[40,50], DM0",
            "14": "[40,50], DM1",
            "15": "[40,50], DM10",
            "16": "[50,70], DM0",
            "17": "[50,70], DM1",
            "18": "[50,70], DM10",
            "19": "[70,], DM0",
            "20": "[70,], DM1",
            "21": "[70,], DM10",
            "100": "cr",
        }
    else:
        logger.fatal("Neither gof variable nor valid categorisation specified.")
        raise Exception

    if args.linear == True:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm"]}

    bkg_processes = {
        "mt": ["VVL", "TTL", "ZL", "jetFakes", "EMB"],
        "mm": ["VV", "TT", "jetFakes", "EMB"]
    }
    if not args.fake_factor and args.embedding:
        bkg_processes = {
            "mt": ["QCD", "VVJ", "W", "TTJ", "ZJ", "ZL", "EMB"],
            "mm": ["VV", "W", "TT", "EMB"]
        }
    if not args.embedding and args.fake_factor:
        bkg_processes = {
            "mt": ["VVT", "VVJ", "TTT", "TTJ", "ZJ", "ZL", "jetFakes", "ZTT"],
            "mm": ["VV", "TT", "jetFakes", "ZLL"]
        }
    if not args.embedding and not args.fake_factor:
        bkg_processes = {
            "mt": ["QCD", "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"],
            "mm": ["VV", "W", "TT", "ZLL"]
        }

    legend_bkg_processes = copy.deepcopy(bkg_processes)
    for chn_bkg_processes in legend_bkg_processes.itervalues():
        chn_bkg_processes.reverse()

    if "2016" in args.era:
        era = "Run2016"
    elif "2017" in args.era:
        era = "Run2017"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    plots = []
    for channel in args.channels:
        for category in channel_categories[channel]:
            rootfile = rootfile_parser.Rootfile_parser(args.input)
            tranche = None
            if "_" in category:
                tranche = category.split("_")[1]
                category = category.split("_")[0]
            # create plot
            width = 600
            if args.linear == True:
                plot = dd.Plot(
                    [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
            else:
                plot = dd.Plot(
                    [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

            # get background histograms
            for process in bkg_processes[channel]:
                plot.add_hist(
                    rootfile.get(era, channel, category, process), process, "bkg")
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])

            # get observed data and total background histograms
            # NOTE: With CMSSW_8_1_0 the TotalBkg definition has changed.
            plot.add_hist(
                rootfile.get(era, channel, category, "data_obs"), "data_obs")
            total_bkg = rootfile.get(era, channel, category, "TotalBkg")
            plot.add_hist(total_bkg, "total_bkg")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.setGraphStyle(
                "total_bkg",
                "e2",
                markersize=0,
                fillcolor=styles.color_dict["unc"],
                linecolor=0)

            plot.subplot(2).normalize([
                "total_bkg", "data_obs"
            ], "total_bkg")

            # stack background processes
            plot.create_stack(bkg_processes[channel], "stack")

            # normalize stacks by bin-width
            if args.normalize_by_bin_width:
                plot.subplot(0).normalizeByBinWidth()
                plot.subplot(1).normalizeByBinWidth()

            # # set axes limits and labels
            plot.subplot(0).setYlims(
                split_dict[channel],
                max(2 * plot.subplot(0).get_hist("total_bkg").GetMaximum(),
                    split_dict[channel] * 2))

            plot.subplot(2).setYlims(0.45, 2.05)

            if args.linear != True:
                plot.subplot(1).setYlims(0.1, split_dict[channel])
                plot.subplot(1).setLogY()
                plot.subplot(1).setYlabel(
                    "")  # otherwise number labels are not drawn on axis
            if args.gof_variable != None:
                if args.gof_variable in styles.x_label_dict[args.channels[0]]:
                    x_label = styles.x_label_dict[args.channels[0]][
                        args.gof_variable]
                else:
                    x_label = args.gof_variable
                plot.subplot(2).setXlabel(x_label)
            else:
                plot.subplot(2).setXlabel("m_{vis} / GeV")
            if args.normalize_by_bin_width:
                plot.subplot(0).setYlabel("dN/d(NN output)")
            else:
                plot.subplot(0).setYlabel("N_{events}")

            plot.subplot(2).setYlabel("")

            #plot.scaleXTitleSize(0.8)
            #plot.scaleXLabelSize(0.8)
            #plot.scaleYTitleSize(0.8)
            plot.scaleYLabelSize(0.8)
            #plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.1)

            #plot.subplot(2).setNYdivisions(3, 5)

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            procs_to_draw = ["stack", "data_obs"] if args.linear else ["stack", "data_obs"]
            plot.subplot(0).Draw(procs_to_draw)
            if args.linear != True:
                plot.subplot(1).Draw([
                    "stack", "data_obs"
                ])
            plot.subplot(2).Draw([
                "total_bkg", "data_obs"
            ])

            # create legends
            suffix = ["", "_top"]
            for i in range(2):
                plot.add_legend(width=0.6, height=0.2)
                for process in legend_bkg_processes[channel]:
                    plot.legend(i).add_entry(
                        0, process, styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV")], 'f')
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

            if args.chi2test:
                import ROOT as r
                f = r.TFile(args.input, "read")
                background = f.Get("htt_{}_{}_Run{}_{}/TotalBkg".format(
                    channel, category, args.era, "prefit"
                    if "prefit" in args.input else "postfit"))
                data = f.Get("htt_{}_{}_Run{}_{}/data_obs".format(
                    channel, category, args.era, "prefit"
                    if "prefit" in args.input else "postfit"))
                chi2 = data.Chi2Test(background, "UW CHI2/NDF")
                plot.DrawText(0.7, 0.3,
                              "\chi^{2}/ndf = " + str(round(chi2, 3)))

            for i in range(2):
                plot.add_legend(
                    reference_subplot=2, pos=1, width=0.5, height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).setNColumns(4)
            plot.legend(2).Draw()
            plot.legend(3).setAlpha(0.0)
            plot.legend(3).Draw()

            # draw additional labels
            plot.DrawCMS()
            if "2016" in args.era:
                plot.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)")
            elif "2017" in args.era:
                plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
            else:
                logger.critical("Era {} is not implemented.".format(args.era))
                raise Exception

            posChannelCategoryLabelLeft = None
            plot.DrawChannelCategoryLabel(
                "%s, %s" % (channel_dict[channel], category_dict[category]),
                begin_left=posChannelCategoryLabelLeft)

            # save plot
            postfix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save("%s_plots/%s_%s_%s_%s.%s" % (args.era, args.era, channel, args.gof_variable if args.gof_variable is not None else category if tranche==None else "_".join([category, tranche]),
                                                postfix, "png"
                                                if args.png else "pdf"))
            plots.append(
                plot
            )  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.INFO)
    main(args)

