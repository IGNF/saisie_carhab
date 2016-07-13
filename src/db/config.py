# -*- coding: utf-8 -*-
class Config:
    """ Namespace for variables and pseudo global functions """
    
    # Db structure. Tables and fields dictionary with standard corresponding:
    DB_STRUCTURE = {"uvc":[
        ("id", "INTEGER PRIMARY KEY", "identifiantUniteCartographiee"),
        ("aut_crea", "TEXT", "auteurCaracterisation", "cache"),
        ("orga_crea", "TEXT", "organismeCaracterisation", "cache"),
        ("date_crea", "TEXT", "dateCaracterisation"),
        ("aut_maj", "TEXT", "auteurMiseAJour", "cache"),
        ("date_maj", "TEXT", "dateMiseAJour"),
        ("cd_src_op", "TEXT", "codeSourceOperateur"),
        ("mode_carac", "TEXT", "modeCaracterisation", "cache"),
        ("mode_obser", "TEXT", "modeObservationVegetation", "cache"),
        ("echelle", "INTEGER", "echelleLeveeCartographique", "cache"),
        ("repr_carto", "TEXT", "representationCartographique", "cache"),
        ("larg_lin", "REAL", "largeurLineaire"),
        ("surface", "REAL", "surface"),
        ("calc_surf", "TEXT", "modeCalculSurface"),
        ("remarque", "TEXT", "remarqueUniteCartographiee")],
    
    "sigmaf":[
        ("id", "INTEGER PRIMARY KEY", "identifiantCompoSigmaFacies"),
        ("sf_catalog", "TEXT", None),
        ("serie_cat", "TEXT", None),
        ("serie_deter", "TEXT", None),
        ("uvc", "INTEGER", "identifiantUniteCartographiee"),
        ("code_serie", "TEXT", "codeSerie"),
        ("lb_serie", "TEXT", "libelleSerie"),
        ("type_cplx", "TEXT", "typeComplexe"),
        ("type_serie", "TEXT", "typeSerie"),
        ("cfc_serie", "TEXT", "confianceSerie"),
        ("code_sigma", "TEXT", "codeSigmaFacies"),
        ("lb_sigma", "TEXT NOT NULL", "libelleSigmaFacies"),
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
        ("cd_syntax", "TEXT NOT NULL", "codeSyntaxon"),
#        ("lb_syntax", "TEXT NOT NULL", None),
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
        
    FORM_STRUCTURE = {"uvc":[
            "aut_crea", "orga_crea", "aut_maj", "mode_carac", "mode_obser", "echelle", "repr_carto"
        ]
    
    }