CREATE TABLE job
	(
		name TEXT PRIMARY KEY,
		aut_crea TEXT,
		orga_crea TEXT,
		date_crea TEXT
	);
	
CREATE TABLE unite_vegetation_cartographiee
	(
		id INTEGER PRIMARY KEY,
		cd_src_op TEXT,
		aut_crea TEXT,
		orga_crea TEXT,
		date_crea TEXT,
		mode_deter TEXT,
		obs_veget TEXT,
		aut_maj TEXT,
		date_maj TEXT,
		echelle INTEGER,
		repr_carto INTEGER,
		larg_lin REAL,
		surface REAL,
		calc_surf TEXT,
		rmq TEXT
	);

CREATE TABLE polygon
	(
		id INTEGER PRIMARY KEY,
		uvc INTEGER,
		lgd_compl INTEGER DEFAULT 0,
		FOREIGN KEY (uvc) REFERENCES unite_vegetation_cartographiee (id)
	);

CREATE TABLE polyline
	(
		id INTEGER PRIMARY KEY,
		uvc INTEGER,
		FOREIGN KEY(uvc) REFERENCES unite_vegetation_cartographiee(id)
	);

CREATE TABLE point
	(
		id INTEGER PRIMARY KEY,
		uvc INTEGER,
		FOREIGN KEY(uvc) REFERENCES unite_vegetation_cartographiee(id)
	);

SELECT AddGeometryColumn('polygon','the_geom',2154,'POLYGON','XY');
SELECT AddGeometryColumn('polyline','the_geom',2154,'LINESTRING','XY');
SELECT AddGeometryColumn('point','the_geom',2154,'POINT','XY');


CREATE TRIGGER check_completion_None AFTER UPDATE ON unite_vegetation_cartographiee
WHEN NEW.cd_src_op = 'None'
AND NEW.aut_crea = 'None'
AND NEW.orga_crea = 'None'
AND NEW.date_crea = 'None'
AND NEW.mode_deter = 'None'
AND NEW.obs_veget = 'None'
AND NEW.aut_maj = 'None'
AND NEW.date_maj = 'None'
AND NEW.echelle = -1
AND NEW.repr_carto = -1
AND NEW.larg_lin = -1.0
AND NEW.surface = -1.0
AND NEW.calc_surf = 'None'
AND NEW.rmq = 'None'

BEGIN
	
UPDATE polygon SET lgd_compl = 0 
WHERE uvc = NEW.id ;

END;

CREATE TRIGGER check_completion_partial AFTER UPDATE ON unite_vegetation_cartographiee
WHEN (
NEW.cd_src_op <> 'None'
OR NEW.aut_crea <> 'None'
OR NEW.orga_crea <> 'None'
OR NEW.date_crea <> 'None'
OR NEW.mode_deter <> 'None'
OR NEW.obs_veget <> 'None'
OR NEW.aut_maj <> 'None'
OR NEW.date_maj <> 'None'
OR NEW.echelle <> -1
OR NEW.repr_carto <> -1
OR NEW.larg_lin <> -1.0
OR NEW.surface <> -1.0
OR NEW.calc_surf <> 'None'
OR NEW.rmq <> 'None'
) AND NOT (
NEW.cd_src_op <> 'None'
AND NEW.aut_crea <> 'None'
AND NEW.orga_crea <> 'None'
AND NEW.date_crea <> 'None'
AND NEW.mode_deter <> 'None'
AND NEW.obs_veget <> 'None'
AND NEW.aut_maj <> 'None'
AND NEW.date_maj <> 'None'
AND NEW.echelle <> -1
AND NEW.repr_carto <> -1
AND NEW.larg_lin <> -1.0
AND NEW.surface <> -1.0
AND NEW.calc_surf <> 'None'
AND NEW.rmq <> 'None'
)


BEGIN
	
UPDATE polygon SET lgd_compl = 1
WHERE uvc = NEW.id ;

END;

CREATE TRIGGER check_completion_Full AFTER UPDATE ON unite_vegetation_cartographiee
WHEN NEW.cd_src_op <> 'None'
AND NEW.aut_crea <> 'None'
AND NEW.orga_crea <> 'None'
AND NEW.date_crea <> 'None'
AND NEW.mode_deter <> 'None'
AND NEW.obs_veget <> 'None'
AND NEW.aut_maj <> 'None'
AND NEW.date_maj <> 'None'
AND NEW.echelle <> -1
AND NEW.repr_carto <> -1
AND NEW.larg_lin <> -1.0
AND NEW.surface <> -1.0
AND NEW.calc_surf <> 'None'
AND NEW.rmq <> 'None'

BEGIN
	
UPDATE polygon SET lgd_compl = 2
WHERE uvc = NEW.id ;

END;