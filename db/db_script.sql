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