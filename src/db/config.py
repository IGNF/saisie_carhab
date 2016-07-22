# -*- coding: utf-8 -*-
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
        ("pct_recouv", "TEXT", "pourcentageRecouvrement")],
	
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
        ("the_geom", "POLYGON", "the_geom")],

    "polyline":[
        ("id", "INTEGER PRIMARY KEY", None),
        ("uvc", "INTEGER", "idUvc"),
        ("lgd_compl", "INTEGER DEFAULT 0", None),
        ("the_geom", "LINESTRING", "the_geom")],

    "point":[
        ("id", "INTEGER PRIMARY KEY", None),
        ("uvc", "INTEGER", "idUvc"),
        ("lgd_compl", "INTEGER DEFAULT 0", None),
        ("the_geom", "POINT", "the_geom")]}

    FORM_STRUCTURE = {
        "uvc":{
            "cbox":[
                ("aut_crea", "auteur", "label"),
                ("aut_maj", "auteur", "label"),
                ("echelle", "echelle", "label"),
                ("orga_crea", "organisme", "label"),
                ("mode_carac", "mode_carac", "label"),
                ("mode_obser", "mode_obser", "label")
            ],"nested_cbox":[
                ("mode_obser", "mode_carac", "caracterisation_observation"),
                ("aut_crea", "orga_crea", "auteur_organisme"),
                ("aut_maj", "orga_crea", "auteur_organisme")
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
                ("typ_facies", "typ_facies", "label"),
                ("typicite", "typicite", "label"),
                ("sat_phy", "sat_phy", "label"),
                ("type_serie", "type_serie", "label"),
                ("type_cplx", "type_cplx", "label"),
                ("code_serie", "serie", "code"),
                ("lb_serie", "serie", "label"),
                ("code_sigma", "sigmaf", "code"),
                ("lb_sigma", "sigmaf", "label")
            ],"linked":[
                ("code_serie", "lb_serie"),
                ("code_sigma", "lb_sigma")
            ]
        },"composyntaxon":{
            "cbox":[
                ("cd_syntax", "syntaxon", "code"),
                ("lb_syntax", "syntaxon", "label"),
                ("abon_domin", "abon_domin", "label"),
                ("code_hic", "HIC", "label"),
                ("mode_carac", "mode_carac_syntax", "label")
            ],"linked":[
                ("cd_syntax", "lb_syntax")
            ]
        }
    }