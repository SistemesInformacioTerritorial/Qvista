# -*- coding: utf-8 -*-

from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery, QSql


class QvSqlite:
    """Clase con métodos estáticos para uso de la geocodificación de Oracle
    """

    @staticmethod
    def coordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas de una dirección postal

        Arguments:
            tipusVia {str} -- Tipo de vía
            nomCarrer {str} -- Nombre o variante de la calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
#        return QvApp().geocod(tipusVia, nomCarrer, '', numIni, lletraIni, numFi, lletraFi)

    @staticmethod
    def coordsCodiNum(codiCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas a partir de código de calle y número postal

        Arguments:
            codiCarrer {str} -- Código de calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
#        return QvApp().geocod('', '', codiCarrer, numIni, lletraIni, numFi, lletraFi)

    @staticmethod
    def normalitzaVariant(variant=''):
        if variant == '' or variant is None:
            return ''

        # Pasar a mayúsculas, eliminar acenttos y otros caracteres, trim
        variant = variant.upper()
        variant = variant.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöü·ºª.',
                                    'AEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOU.   ')
        variant = variant.strip()
        if variant == '':
            return variant

        # Eliminar espacions en blanco redundantes
        tmp = variant.replace('  ', ' ')
        while tmp != variant:
            variant = tmp
            tmp = variant.replace('  ', ' ')

        # Las variantes tienen como máximo 30 caracteres
        if len(variant) > 30:
            variant = variant[0:30]




        return variant


#    -------------------------------------------------------------------------------------------
#    -- ( fNormalizaVariante ) --------------------------------------------------------------
#    -------------------------------------------------------------------------------------------
#    -- Entorno : Privada --------------------------------------------------------------------
#    -- Parametros : pVARIANTE        ( Entrada - Variante a tratar )
#    -- Retorno :    pRESULTADO ->    Variante resultante ya tratada
#    -- Función : Retorna la variante despues de realizar algunos tratamientos con ella :
#    --           1 -> Paso a Mayusculas
#    --           2 -> Supresión de espacios en blanco al principio y al final de la variante
#    --           3 -> Sustitución de grupos de espacios en blanco en media de la variante
#    --                por un solo espacio
#    --           4 -> Sustitución de acentos, dieresis y puntuación de la 'l ageminada'
#    --           5 -> Si se encuentra un espacio en blanco en la variante, se supone que
#    --                el tipo de via es la primera palabra. Se busca edsta palabra en el
#    --                variantero de tipos de via y si se encuentra se sustituye por el
#    --                tipo de via oficial, si no se encuentra se retorna la variante
#    --                como este.
#    -------------------------------------------------------------------------------------------
#    FUNCTION fNormalizaVariante (pVARIANTE IN VARCHAR2)
#       RETURN VARCHAR2
#    IS
#    BEGIN
#       DECLARE
#          sVARIANTE      VARCHAR2 (256);
#          sVARTIPUSVIA   VARCHAR2 (256);
#          sPARTICULA     VARCHAR2 (256);
#          sTIPUSVIA      VARCHAR2 (256);
#          sTMP           VARCHAR2 (256);
#          nPos           INTEGER;
#       BEGIN
#          -- Conversión a Mayusculas
#          sVARIANTE := UPPER (pVARIANTE);
#          -- Sustitución de puntos por blancos'
#          sVARIANTE := TRANSLATE (sVARIANTE, '.', ' ');
#          -- Sustitución de acentos, dieresis y puntuación de la 'l ageminada'
#          sVARIANTE :=
#             TRANSLATE (
#                sVARIANTE,
#                'ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöü·ºª',
#                'AEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOU.  ');
#          -- Eliminación de espacios al principio y al final
#          sVARIANTE := LTRIM (RTRIM (sVARIANTE));

#          IF (sVARIANTE = '') OR (sVARIANTE IS NULL)
#          THEN
#             RETURN '';
#          END IF;

#          -- Eliminación de espacios en blanco redundantes
#          sTMP := '';

#          LOOP
#             sTMP := REPLACE (sVARIANTE, '  ', ' ');

#             IF sTMP = sVARIANTE
#             THEN
#                sVARIANTE := sTMP;
#                EXIT;
#             END IF;

#             sVARIANTE := sTMP;
#          END LOOP;

#          -- Se hace por la limitación existente a 30 caracteres y la salvedad de
#          -- 'Gran Via de les Corts Catalanes''
#          IF LENGTH (sVARIANTE) > 30
#          THEN
#             sVARIANTE := SUBSTR (sVARIANTE, 1, 30);
#          END IF;

#          nPos := INSTR (sVARIANTE, ' ');

#          -- Se encuentran varias palabras en la variante, se toma la primera como tipo de via
#          IF nPos > 0
#          THEN
#             -- Previo al tratamiento del tipo de via, se busca la variante exacta
#             -- Esto se realiza ya que existen calles en cuyo nombre existe como parte
#             -- del nombre un tipo a variante de tipo de vial.
#             -- Si se encuentra la variante exacta, no se procesa el tipo de vial.
#             BEGIN
#                -- Se quita el posible comodin para la búsqueda exacta
#                SELECT CODI
#                  INTO sTMP
#                  FROM VARIANTS
#                 WHERE VARIANT = REPLACE (sVARIANTE, '%', '');

#                RETURN sVARIANTE;
#             EXCEPTION
#                WHEN NO_DATA_FOUND
#                THEN
#                   NULL;
#                WHEN OTHERS
#                THEN
#                   NULL;
#             END;

#             sVARTIPUSVIA := SUBSTR (sVARIANTE, 1, nPos - 1);

#             BEGIN
#                SELECT TIPUS_VIA
#                  INTO sTIPUSVIA
#                  FROM VAR_TIPUSVIA
#                 WHERE VARIANT = sVARTIPUSVIA;
#             EXCEPTION
#                WHEN NO_DATA_FOUND
#                THEN
#                   RETURN sVARIANTE;
#                WHEN OTHERS
#                THEN
#                   RETURN sVARIANTE;
#             END;

#             sVARIANTE :=
#                LTRIM (
#                   SUBSTR (sVARIANTE, nPos, (LENGTH (sVARIANTE) - nPos) + 1));

#             -- Se buscan las particulas 'DE', 'DEL', 'DELS', 'D'EN', 'D'', 'DE L'', 'DE LA', 'DE LES', 'DE LOS' Y 'DE LAS'

#             sPARTICULA := SUBSTR (sVARIANTE, 1, 2);

#             IF sPARTICULA = 'D'''
#             THEN
#                sPARTICULA := SUBSTR (sVARIANTE, 1, 5);

#                IF sPARTICULA <> 'D''EN '
#                THEN
#                   sVARIANTE :=
#                      LTRIM (SUBSTR (sVARIANTE, 3, (LENGTH (sVARIANTE) - 2)));
#                END IF;
#             END IF;

#             nPos := INSTR (sVARIANTE, ' ');

#             IF nPos > 0
#             THEN
#                sPARTICULA := SUBSTR (sVARIANTE, 1, nPos - 1);

#                IF sPARTICULA = 'DE'
#                THEN
#                   sVARIANTE :=
#                      LTRIM (
#                         SUBSTR (sVARIANTE,
#                                 nPos,
#                                 (LENGTH (sVARIANTE) - nPos) + 1));

#                   -- Busqueda de 'DE L''
#                   sPARTICULA := SUBSTR (sVARIANTE, 1, 2);

#                   IF sPARTICULA = 'L'''
#                   THEN
#                      sVARIANTE :=
#                         LTRIM (
#                            SUBSTR (sVARIANTE, 3, (LENGTH (sVARIANTE) - 2)));
#                   ELSE
#                      nPos := INSTR (sVARIANTE, ' ');

#                      IF nPos > 0
#                      THEN
#                         sPARTICULA := SUBSTR (sVARIANTE, 1, nPos - 1);

#                         IF    sPARTICULA = 'LA'
#                            OR sPARTICULA = 'LES'
#                            OR sPARTICULA = 'LOS'
#                            OR sPARTICULA = 'LAS'
#                         THEN
#                            sVARIANTE :=
#                               LTRIM (
#                                  SUBSTR (sVARIANTE,
#                                          nPos,
#                                          (LENGTH (sVARIANTE) - nPos) + 1));
#                         END IF;
#                      END IF;
#                   END IF;
#                ELSIF    sPARTICULA = 'DEL'
#                      OR sPARTICULA = 'DELS'
#                      OR sPARTICULA = 'D''EN'
#                THEN
#                   sVARIANTE :=
#                      LTRIM (
#                         SUBSTR (sVARIANTE,
#                                 nPos,
#                                 (LENGTH (sVARIANTE) - nPos) + 1));
#                END IF;
#             END IF;

#             IF sTIPUSVIA <> 'C'
#             THEN
#                sVARIANTE := sTIPUSVIA || ' ' || sVARIANTE;
#             END IF;
#          END IF;

#          RETURN sVARIANTE;
#       END;
#    END;
#    -------------------------------------------------------------------------------------------



if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        x, y = QvSqlite.coordsCodiNum('001808', '23', '', '25')
        if x is None or y is None:
            print('No coords')
        else:
            print('001808', '23', '25', str(x), str(y))

        x, y = QvSqlite.coordsCodiNum('003406', '132', 'B')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvSqlite.coordsCodiNum('dfadfadfadfadf', 'asdfadfad')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvSqlite.coordsCarrerNum('C', 'Mallorca', '100')
        if x is None or y is None:
            print('No coords')
        else:
            print('C', 'Mallorca', '100', str(x), str(y))

        x, y = QvSqlite.coordsCarrerNum('', 'Balmes', '150')
        if x is None or y is None:
            print('No coords')
        else:
            print('Balmes', '150', str(x), str(y))

        x, y = QvSqlite.coordsCarrerNum('Av', 'Diagonal', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '220', str(x), str(y))

        x, y = QvSqlite.coordsCarrerNum('Av', 'Diagonal', '45', 'X')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '45', 'X', str(x), str(y))

        x, y = QvSqlite.coordsCarrerNum('', 'Msakjdaskjdlasdj', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Msakjdaskjdlasdj', '220', str(x), str(y))
