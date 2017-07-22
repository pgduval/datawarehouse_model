
CREATE TABLE dim1 (
                id_dim1 INT AUTO_INCREMENT NOT NULL,
                attribute1 VARCHAR(5) NOT NULL,
                PRIMARY KEY (id_dim1)
);


CREATE TABLE dim2 (
                id_dim2 INT AUTO_INCREMENT NOT NULL,
                attribute1 VARCHAR(5) NOT NULL,
                PRIMARY KEY (id_dim2)
);


CREATE TABLE fact1 (
                id_fact1 INT AUTO_INCREMENT NOT NULL,
                id_dim1 INT NOT NULL,
                id_dim2 INT NOT NULL,
                metric1 NUMERIC(11,2) NOT NULL,
                PRIMARY KEY (id_fact1)
);


ALTER TABLE fact1 ADD CONSTRAINT dim1_fact1_fk
FOREIGN KEY (id_dim1)
REFERENCES dim1 (id_dim1)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE fact1 ADD CONSTRAINT dim2_fact1_fk
FOREIGN KEY (id_dim2)
REFERENCES dim2 (id_dim2)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
