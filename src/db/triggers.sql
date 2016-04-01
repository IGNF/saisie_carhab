CREATE TRIGGER check_completion_None AFTER UPDATE ON uvc
WHEN NEW.aut_crea IS NULL
AND NEW.orga_crea IS NULL
AND NEW.mode_carac IS NULL
AND NEW.mode_obser IS NULL
AND NEW.echelle IS NULL

BEGIN
	
UPDATE polygon SET lgd_compl = 0 
WHERE uvc = NEW.id ;

END;




CREATE TRIGGER check_completion_partial AFTER UPDATE ON uvc
WHEN (
NEW.aut_crea IS NOT NULL
OR NEW.orga_crea IS NOT NULL
OR NEW.mode_carac IS NOT NULL
OR NEW.mode_obser IS NOT NULL
OR NEW.echelle IS NOT NULL
) AND NOT (
NEW.aut_crea IS NOT NULL
AND NEW.orga_crea IS NOT NULL
AND NEW.mode_carac IS NOT NULL
AND NEW.mode_obser IS NOT NULL
AND NEW.echelle IS NOT NULL
)

BEGIN

UPDATE polygon SET lgd_compl = 1
WHERE uvc = NEW.id ;

END;




CREATE TRIGGER check_completion_Full AFTER UPDATE ON uvc
WHEN NEW.aut_crea IS NOT NULL
AND NEW.orga_crea IS NOT NULL
AND NEW.mode_carac IS NOT NULL
AND NEW.mode_obser IS NOT NULL
AND NEW.echelle IS NOT NULL




BEGIN

UPDATE polygon SET lgd_compl = 2
WHERE uvc = NEW.id ;

END;




CREATE TRIGGER create_uvc AFTER INSERT ON polygon

BEGIN

INSERT INTO uvc (surface) VALUES (ST_AREA(NEW.the_geom));
UPDATE polygon SET uvc = (SELECT id FROM uvc ORDER BY id DESC LIMIT 1)
WHERE id = NEW.id;


END;