# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class Config:
    """ Namespace for variables and pseudo global functions """
    
    # Db structure. Tables and fields dictionary with corresponding standard :
    DB_STRUCTURE = {"uvc":[
        ("id", "INTEGER PRIMARY KEY", "identifiantUniteCartographiee"),
        ("aut_crea", "TEXT", "auteurCaracterisation"),
        ("orga_crea", "TEXT", "organismeCaracterisation"),
        ("date_crea", "TEXT", "dateCaracterisation"),
        ("aut_maj", "TEXT", "auteurMiseAJour"),
        ("date_maj", "TEXT", "dateMiseAJour"),
        ("cd_src_op", "TEXT", "codeSourceOperateur"),
        ("mode_carac", "TEXT", "modeCaracterisation"),
        ("mode_obser", "TEXT", "modeObservationVegetation"),
        ("echelle", "INTEGER", "echelleLeveeCartographique"),
        ("repr_carto", "TEXT", "representationCartographique"),
        ("larg_lin", "REAL", "largeurLineaire"),
        ("surface", "REAL", "surface"),
        ("calc_surf", "TEXT", "modeCalculSurface"),
        ("remarque", "TEXT", "remarqueUniteCartographiee")],
    
    "sigmaf":[
        ("id", "INTEGER PRIMARY KEY", "identifiantCompoSigmaFacies"),
        ("catalog", "TEXT", None),
        ("serie_cat", "TEXT", None),
        ("serie_deter", "TEXT", None),
        ("uvc", "INTEGER", "identifiantUniteCartographiee"),
        ("code_serie", "TEXT", "codeSerie"),
        ("lb_serie", "TEXT", "libelleSerie"),
        ("type_cplx", "TEXT", "typeComplexe"),
        ("type_serie", "TEXT", "typeSerie"),
        ("cfc_serie", "TEXT", "confianceSerie"),
        ("code_sigma", "TEXT", "codeSigmaFacies"),
        ("lb_sigma", "TEXT", "libelleSigmaFacies"),
        ("typ_facies", "TEXT", "typeFacies"),
        ("rmq_typ_fa", "TEXT", "remarqueTypeFacies"),
        ("typicite", "TEXT", "typiciteSigmaFacies"),
        ("rmq_typcte", "TEXT", "remarqueTypiciteFacies"),
        ("sat_phy", "TEXT", "saturationPhytocenotique"),
        ("rmq_sat_ph", "TEXT", "remarqueSaturationPhytocenotique"),
        ("cfc_facies", "TEXT", "confianceFacies"),
        ("pct_recouv", "INTEGER", "pourcentageRecouvrement")],
	
    "composyntaxon":[
        ("id", "INTEGER PRIMARY KEY", "identifiantCompoReelleSyntaxons"),
        ("uvc", "INTEGER", "identifiantUniteCartographiee"),
        ("sigmaf", "INTEGER", "identifiantCompoSigmaFacies"),
        ("cd_syntax", "TEXT", "codeSyntaxon"),
        ("lb_syntax", "TEXT", "libelleSyntaxon"),
        ("abon_domin", "TEXT", "abondanceDominance"),
        ("dominance", "TEXT", "dominance"),
        ("code_hic", "TEXT", "codeHIC"),
        ("mode_carac", "TEXT", "modeCaracterisation"),
        ("remarque", "TEXT", "remarque")],


    "polygon":[
        ("id", "INTEGER PRIMARY KEY", None),
        ("uvc", "INTEGER", "uvc"),
        ("lgd_compl", "INTEGER DEFAULT 0", None),
        ("pct_facies", "TEXT", None),
        ("the_geom", "POLYGON", "the_geom")],

    "polyline":[
        ("id", "INTEGER PRIMARY KEY", None),
        ("uvc", "INTEGER", "idUvc"),
        ("lgd_compl", "INTEGER DEFAULT 0", None),
        ("pct_facies", "TEXT", None),
        ("the_geom", "LINESTRING", "the_geom")],

    "point":[
        ("id", "INTEGER PRIMARY KEY", None),
        ("uvc", "INTEGER", "idUvc"),
        ("lgd_compl", "INTEGER DEFAULT 0", None),
        ("pct_facies", "TEXT", None),
        ("the_geom", "POINT", "the_geom")]}

    FORM_STRUCTURE = {
        "uvc":{
            "cbox":[
                ("aut_crea", "auteur", "label", "code"),
                ("aut_maj", "auteur", "label", "code"),
                ("echelle", "echelle", "label", "code"),
                ("orga_crea", "organisme", "label", "code"),
                ("mode_carac", "mode_carac", "label", "code"),
                ("mode_obser", "mode_obser", "label", "code")
            ],"nested_cbox":[
                ("mode_carac", "code_parent", "mode_obser", "code_child", "caracterisation_observation"),
                ("orga_crea", "code_parent", "aut_crea", "code_child", "auteur_organisme"),
                ("orga_crea", "code_parent", "aut_maj", "code_child", "auteur_organisme")
            ],"cache":[
                "aut_crea",
                "orga_crea",
                "aut_maj",
                "mode_carac",
                "mode_obser",
                "echelle",
                "repr_carto"
            ]
        },"sigmaf":{
            "cbox":[
                ("typ_facies", "typ_facies", "label", "code"),
                ("typicite", "typicite", "label", "code"),
                ("sat_phy", "sat_phy", "label", "code"),
                ("type_serie", "type_serie", "label", "code"),
                ("type_cplx", "type_cplx", "label", "code"),
                ("code_serie", "serie", "LB_CODE", "LB_CODE"),
                ("lb_serie", "serie", "LB_HAB_FR_COMPLET", "LB_CODE"),
                ("code_sigma", "sigmaf", "LB_CODE", "LB_CODE"),
                ("lb_sigma", "sigmaf", "LB_HAB_FR_COMPLET", "LB_CODE")
            ],"linked":[
                ("code_serie", "lb_serie"),
                ("code_sigma", "lb_sigma")
            ],"nested_cbox":[
                ("code_sigma", "LB_CODE_GSF", "code_serie", "LB_CODE_GS", "serie_sigmaf"),
                ("lb_sigma", "LB_CODE_GSF", "lb_serie", "LB_CODE_GS", "serie_sigmaf")
            ]
        },"composyntaxon":{
            "cbox":[
                ("cd_syntax", "syntaxon", "LB_CODE", "LB_CODE"),
                ("lb_syntax", "syntaxon", "LB_HAB_FR_COMPLET", "LB_CODE"),
                ("abon_domin", "abon_domin", "label", "code"),
                ("code_hic", "HIC", "label", "code"),
                ("mode_carac", "mode_carac_syntax", "label", "code")
            ],"linked":[
                ("cd_syntax", "lb_syntax")
            ],"nested_cbox":[
                ("cd_syntax", "CD_HAB_ENTRE", "code_hic", "CD_HAB_SORTIE", "CRSP_PVF2_HIC_20")
            ]
        }
    }
    
    CATALOG_STRUCTURE = {
        "data":{
            "sigmaf":[
                "LB_CODE",
                "LB_HAB_FR_COMPLET",
                "LB_HAB_FR",
                "LB_NIVEAU",
                "CD_HAB_SUP"
            ], "syntaxon":[
                "LB_CODE",
                "LB_HAB_FR_COMPLET",
                "LB_HAB_FR",
                "LB_NIVEAU",
                "CD_HAB_SUP"
            ], "serie": [
                "LB_CODE",
                "LB_HAB_FR_COMPLET",
                "LB_HAB_FR",
                "LB_NIVEAU",
                "CD_HAB_SUP"
            ],
        }, "links":{
            "serie_sigmaf":[
                ("serie", "LB_CODE", "LB_CODE_GS"),
                ("sigmaf", "LB_CODE", "LB_CODE_GSF")
            ], "sigmaf_syntaxon":[
                ("sigmaf", "LB_CODE", "LB_CODE_GSF"),
                ("syntaxon", "LB_CODE", "LB_CODE_SYNTAXON")
            ]
        }
    }