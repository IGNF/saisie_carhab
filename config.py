# -*- coding: utf-8 -*-

from __future__ import unicode_literals

""" Namespace for variables and pseudo global functions """

PROJECT_NAME = 'carhab'

CRS_CODE = 2154

# Db structure. Tables and fields dictionary with corresponding standard :
#    (
#        (
#            "table_name_in_db",{
#                ["label": "a_human_readable_label_for_the_table"]
#                ["std_name": "name_of_standard_csv_file"]
#                "fields":(
#                    (
#                        "name_of_the_field_in_the_db", {
#                            "type": ["TEXT [DEFAULT String", "INTEGER [DEFAULT Int] | [PRIMARY KEY]", "REAL [DEFAULT Double]", "POLYGON", "LINESTRING", "POINT"]
#                            ["std_name": "field_name_in_standard_csv_file]
#                            "cache": True | False. To keep filled value in memory for next acquisitions (default False)
#                            "spatial": True | False. Table is spatial or not (default False)
#                        }
#                    ),(
#                        [....]
#                    )
#                )
#            }
#        ),(
#            [....]
#        )
#    )
def get_table_info(table_name):
    for tbl_n, desc in DB_STRUCTURE:
        if tbl_n == table_name:
            return desc

def get_table_fields(table_name):
    return [desc.get('fields') for tbl_n, desc in DB_STRUCTURE if tbl_n == table_name][0]

def get_spatial_tables():
    return [tbl_n for tbl_n, desc in DB_STRUCTURE if desc.get('spatial')]
            
def get_no_spatial_tables():
    return [tbl_n for tbl_n, desc in DB_STRUCTURE if not desc.get('spatial')]

def get_spatial_column(table_name):
    res = []
    if table_name in get_spatial_tables():
        res = [fld_n for fld_n, desc in get_table_info(table_name).get('fields') if desc.get('spatial')][0]
    return res

DB_STRUCTURE = ((
    "uvc",{
        "label": "UVC",
        "std_name": "St_UniteCarto_Description",
        "fields":((
            "id",{
                "type": "INTEGER PRIMARY KEY",
                "std_name": "identifiantUniteCartographiee"
            }),(
            "orga_crea",{
                "type": "TEXT",
                "std_name": "organismeCaracterisation",
                "cache": True
            }),(
            "date_crea",{
                "label": "Date de caractérisation",
                "type": "TEXT",
                "std_name": "dateCaracterisation"
            }),(
            "aut_crea",{
                "label": "Auteur de la caractérisation",
                "type": "TEXT",
                "std_name": "auteurCaracterisation",
                "cache": True
            }),(
            "orga_maj",{
                "type": "TEXT",
                "std_name": "organismeMiseAJour",
                "cache": True
            }),(
            "aut_maj",{
                "label": "Auteur de la mise à jour",
                "type": "TEXT",
                "std_name": "auteurMiseAJour",
                "cache": True
            }),(
            "date_maj",{
                "label": "Date de mise à jour",
                "type": "TEXT",
                "std_name": "dateMiseAJour"
            }),(
            "cd_src_op",{
                "type": "TEXT",
                "std_name": "codeSourceOperateur"
            }),(
            "mode_carac",{
                "type": "TEXT",
                "std_name": "modeCaracterisation",
                "cache": True
            }),(
            "mode_obser",{
                "type": "TEXT",
                "std_name": "modeObservationVegetation",
                "cache": True
            }),(
            "echelle",{
                "order": 10,
                "type": "INTEGER",
                "std_name": "echelleLeveeCartographique",
                "cache": True
            }),(
            "repr_carto",{
                "label": "Représentation au 25000ème",
                "type": "TEXT",
                "std_name": "representationCartographique",
                "cache": True
            }),(
            "larg_lin",{
                "type": "REAL",
                "std_name": "largeurLineaire"
            }),(
            "surface",{
                "type": "REAL",
                "std_name": "surface"
            }),(
            "calc_surf",{
                "type": "TEXT",
                "std_name": "modeCalculSurface"
            }),(
            "remarque",{
                "type": "TEXT",
                "std_name": "remarqueUniteCartographiee"
            })
        )
    }),(
    "sigmaf",{
        "label": "Composition en Sigmafacies",
        "std_name": "St_CompoSigmaFacies",
        "fields": (
            ("id",{
                "type": "INTEGER PRIMARY KEY",
                "std_name": "identifiantCompoSigmaFacies"
            }),(
            "catalog",{
                "type": "TEXT",
                "std_name": "sigmaFaciesDeCatalogue"
            }),(
            "serie_cat",{
                "type": "TEXT",
                "std_name": "serieDeCatalogue"
            }),(
            "serie_deter",{
                "type": "TEXT",
                "std_name": "serieDeterminee"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "identifiantUniteCartographiee"
            }),(
            "code_sigma",{
                "type": "TEXT",
                "std_name": "codeSigmaFacies"
            }),(
            "lb_sigma",{
                "type": "TEXT",
                "std_name": "libelleSigmaFacies"
            }),(
            "code_serie",{
                "type": "TEXT",
                "std_name": "codeSerie",
                "label": "Code de la série"
            }),(
            "lb_serie",{
                "type": "TEXT",
                "std_name": "libelleSerie",
                "label": "Libellé de la série"
            }),(
            "type_cplx",{
                "type": "TEXT",
                "std_name": "typeComplexe"
            }),(
            "type_serie",{
                "type": "TEXT",
                "std_name": "typeSerie"
            }),(
            "cfc_serie",{
                "type": "TEXT",
                "std_name": "confianceSerie"
            }),(
            "typ_facies",{
                "label": "Type de facies",
                "type": "TEXT",
                "std_name": "typeFacies"
            }),(
            "rmq_typ_fa",{
                "label": "Remarque sur le type de facies",
                "type": "TEXT",
                "std_name": "remarqueTypeFacies"
            }),(
            "typicite",{
                "type": "TEXT DEFAULT 'nr'",
                "std_name": "typiciteSigmaFacies"
            }),(
            "rmq_typcte",{
                "label": "Remarque sur la typicité",
                "type": "TEXT",
                "std_name": "remarqueTypiciteFacies"
            }),(
            "sat_phy",{
                "type": "TEXT",
                "std_name": "saturationPhytocenotique"
            }),(
            "rmq_sat_ph",{
                "label": "Remarque sur la saturation phytocénotique",
                "type": "TEXT",
                "std_name": "remarqueSaturationPhytocenotique"
            }),(
            "cfc_facies",{
                "type": "TEXT",
                "std_name": "confianceFacies"
            }),(
            "pct_recouv",{
                "label": "% de recouvrement",
                "type": "INTEGER",
                "std_name": "pourcentageRecouvrement"
            })
        )
    }),(
    "composyntaxon",{
        "label":"Composition en Syntaxons",
        "std_name": "St_CompoReelleSyntaxons",
        "fields":(("id",{
                "type": "INTEGER PRIMARY KEY",
                "std_name": "identifiantCompoReelleSyntaxons"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "identifiantUniteCartographiee"
            }),(
            "sigmaf",{
                "type": "INTEGER",
                "std_name": "identifiantCompoSigmaFacies"
            }),(
            "cd_syntax",{
                "type": "TEXT",
                "std_name": "codeSyntaxon",
                "label": "Code du syntaxon"
            }),(
            "lb_syntax",{
                "type": "TEXT",
                "std_name": "libelleSyntaxon",
                "label": "Libellé du syntaxon"
            }),(
            "abon_domin",{
                "label": "Abondance / dominance",
                "type": "TEXT"
            }),(
            "cd_ab_dom",{
                "label": "Coeff. abondance / dominance",
                "type": "TEXT",
                "std_name": "abondanceDominance"
            }),(
            "dominance",{
                "type": "TEXT",
                "std_name": "dominance"
            }),(
            "code_hic",{
                "type": "TEXT",
                "std_name": "codeHIC"
            }),(
            "label_hic",{
                "type": "TEXT"
            }),(
            "mode_carac",{
                "type": "TEXT",
                "std_name": "modeCaracterisation"
            }),(
            "remarque",{
                "label": "Remarque sur le syntaxon",
                "type": "TEXT",
                "std_name": "remarque"
            })
        )
    }),(
    "attributsadd",{
        "label":"Attributs additionnels",
        "std_name": "St_UVC_AttributsAdd",
        "fields":((
            "id",{
                "type": "INTEGER PRIMARY KEY"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "identifiantUniteCartographiee"
            }),(
            "lb_attr",{
                "label": "Libellé",
                "type": "TEXT",
                "std_name": "libelleAttribut"
            }),(
            "unite",{
                "label": "Unité",
                "type": "TEXT",
                "std_name": "uniteAttribut"
            }),(
            "valeur",{
                "label": "Valeur",
                "type": "TEXT",
                "std_name": "valeurAttribut"
            })
        )
    }),(
    "point",{
        "label":"Couche des points",
        "std_name": "St_SIG_point",
        "spatial": True,
        "fields":((
            "id",{
                "type": "INTEGER PRIMARY KEY"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "uvc"
            }),(
            "lgd_compl",{
                "type": "INTEGER DEFAULT 0"
            }),(
            "pct_facies",{
                "type": "TEXT"
            }),(
            "the_geom",{
                "type": "POINT",
                "spatial": True
            })
        )
    }),(
    "polyline",{
        "label":"Couche des polylignes",
        "std_name": "St_SIG_polyline",
        "spatial": True,
        "fields":((
            "id",{
                "type": "INTEGER PRIMARY KEY"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "uvc"
            }),(
            "lgd_compl",{
                "type": "INTEGER DEFAULT 0"
            }),(
            "pct_facies",{
                "type": "TEXT"
            }),(
            "the_geom",{
                "type": "LINESTRING",
                "spatial": True
            })
        )
    }),(
    "polygon",{
        "label":"Couche des polygones",
        "std_name": "St_SIG_polygon",
        "spatial": True,
        "fields":((
            "id",{
                "type": "INTEGER PRIMARY KEY"
            }),(
            "uvc",{
                "type": "INTEGER",
                "std_name": "uvc"
            }),(
            "lgd_compl",{
                "type": "INTEGER DEFAULT 0"
            }),(
            "pct_facies",{
                "type": "TEXT"
            }),(
            "the_geom",{
                "type": "POLYGON",
                "spatial": True
            })
        )
    })
)


FORM_STRUCTURE = {
    "uvc":{
        "cbox":[
            #("field name", "csv file name", "field to display name", "field code name", "value name to record into db")
            ("orga_crea", "organisme", "label", "code"),
            ("orga_maj", "organisme", "label", "code"),
            ("aut_crea", "auteur", "label", "code"),
            ("aut_maj", "auteur", "label", "code"),
            ("echelle", "echelle", "label", "code"),
            ("mode_carac", "mode_carac", "label", "code"),
            ("mode_obser", "mode_obser", "label", "code")
        ],"nested_cbox":[
            ("orga_crea", "code_parent", "aut_crea", "code_child", "auteur_organisme"),
            ("mode_carac", "code_parent", "mode_obser", "code_child", "caracterisation_observation"),
            ("orga_maj", "code_parent", "aut_maj", "code_child", "auteur_organisme")
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
            ("cd_ab_dom", "abon_domin", "valeur", "code"),
            ("abon_domin", "abon_domin", "label", "code"),
            ("code_hic", "HIC", "code_hic", "code"),
            ("label_hic", "HIC", "label", "code"),
            ("mode_carac", "mode_carac_syntax", "label", "code")
        ],"linked":[
            ("cd_syntax", "lb_syntax"),
            ("code_hic", "label_hic"),
            ("cd_ab_dom", "abon_domin")
        ],"nested_cbox":[
            ("cd_syntax", "CD_HAB_ENTRE", "code_hic", "CD_HAB_SORTIE", "CRSP_PVF2_HIC_20"),
            ("cd_syntax", "CD_HAB_ENTRE", "label_hic", "CD_HAB_SORTIE", "CRSP_PVF2_HIC_20")
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