from __future__ import division

import json
import unittest
import geoprocessing
import geo_utils
import numpy as np

from copy import copy
from shapely import wkt
from shapely.geometry import mapping, Point, Polygon, shape
from shapely.geometry.geo import box

NLCD_PATH = '../test_data/philly_nlcd.tif'
NLCD_EDIT_PATH = '../test_data/philly_nlcd_edited.tif'
NLCD_ONES = '../test_data/philly_ones.tif'      # all cells are 1
NLCD_THREES = '../test_data/philly_threes.tif'  # all cells are 3
NLCD_LARGE = '../test_data/nlcd_large.tif'


class CountTests(unittest.TestCase):
    count_geom = Polygon([
        [1747260.99651947943493724, 2071928.23170474520884454],
        [1747260.99651947943493724, 2071884.15942327585071325],
        [1747323.9569215786177665, 2071882.06074320594780147],
        [1747321.85824150871485472, 2071927.53214472183026373],
        [1747260.99651947943493724, 2071928.23170474520884454]])

    expectedCounts = {'11': 2, '24': 2, '23': 2}

    def test_count(self):
        """
        Tests the count of a known polygon against the NLCD raster
        to verify the correct number of values are counted
        """
        total, counts = geoprocessing.count(self.count_geom, NLCD_PATH)

        self.assertEqual(total, 6)
        self.assertDictEqual(counts, self.expectedCounts)

    def test_count_with_mods(self):
        """
        Tests the count of a known polygon after modifications to a
        source raster have been made
        """
        # Change the area of the source raster that has a value of 11 to 42
        # within this polygon, which is a a subset of the AoI
        modificationPolygon = Polygon([
            [1747265.19387961947359145, 2071930.33038481511175632],
            [1747265.19387961947359145, 2071890.45546348579227924],
            [1747250.50311912968754768, 2071889.75590346241369843],
            [1747251.20267915306612849, 2071927.53214472183026373],
            [1747250.50311912968754768, 2071927.53214472183026373],
            [1747265.19387961947359145, 2071930.33038481511175632]])

        mods = [{'geom': modificationPolygon, 'newValue': 42}]

        # Expect the base counts but with all values of 11 changed to 42
        modifiedCounts = copy(self.expectedCounts)
        modifiedCounts['42'] = modifiedCounts.pop('11')

        total, counts = geoprocessing.count(self.count_geom, NLCD_PATH, mods)

        self.assertEqual(total, 6)
        self.assertDictEqual(counts, modifiedCounts)

    def test_pair_count(self):
        """
        Test the count of a known polygon against two edited rasters
        to verify that the correct pairs of values are counted
        """
        geom = Polygon([
            [1747247.00531901302747428, 2071931.02994483849033713],
            [1747248.4044390597846359, 2071849.88098213309422135],
            [1747333.05120188184082508, 2071848.48186208633705974],
            [1747333.05120188184082508, 2071931.02994483849033713],
            [1747247.00531901302747428, 2071931.02994483849033713]])

        expectedPairs = {
            '11::44': 2, '11::55': 1, '11::33': 1,
            '23::77': 2, '24::99': 1, '24::88': 2
        }
        pairs = geoprocessing.count_pairs(geom, [NLCD_PATH, NLCD_EDIT_PATH])

        self.assertDictEqual(pairs, expectedPairs)


class SamplingTests(unittest.TestCase):
    def test_xy(self):
        """
        Tests the value of a known point againt the NLCD raster
        to verify the cell value at the point is correct
        """
        geom = Point(1747240.00972, 2071756.8395)
        value = geoprocessing.sample_at_point(geom, NLCD_PATH)

        self.assertEqual(value, 11)


class FeatureTests(unittest.TestCase):
    def test_water(self):
        """
        Tests the value of a known point againt the NLCD raster
        to verify the cell value at the point is correct
        """
        geom = Polygon([
            [1747247.00531901302747428, 2071931.02994483849033713],
            [1747248.4044390597846359, 2071849.88098213309422135],
            [1747333.05120188184082508, 2071848.48186208633705974],
            [1747333.05120188184082508, 2071931.02994483849033713],
            [1747247.00531901302747428, 2071931.02994483849033713]])

        values = geoprocessing.extract(geom, NLCD_PATH, 11)
        out = [json.dumps(mapping(
               geo_utils.reproject(shape(feature), 'epsg:4326', 'epsg:5070')))
               for feature in values]

        self.assertEqual(out, 11)

    def test_levee(self):

        geom_del = wkt.loads("""
            POLYGON ((-75.20484924316406 39.878390675246706, -75.18905639648438 39.8725941278615, -75.17601013183592 39.87812720644829, -75.17189025878906 39.87812720644829, -75.16983032226562 39.87970800405549, -75.15472412109375 39.87786373663762, -75.14545440673828 39.87891760980689, -75.13412475585938 39.88365983864681, -75.12828826904297 39.89577737784395, -75.1351547241211 39.89841134204854, -75.14202117919922 39.88813830918363, -75.16124725341797 39.88787487783849, -75.19248962402344 39.885240508711654, -75.20484924316406 39.878390675246706))
        """)
        geom_pitts = wkt.loads("""
            POLYGON ((-80.089941828125 40.45093583124998 0.000010000001099, -80.08968020468751 40.448662134374956 0.000010000001099, -80.08966002968754 40.448670092187456 0.000010000001099, -80.08936905000002 40.44786454218746 0.000010000001099, -80.08817721874999 40.44639971718749 0.000010000001099, -80.08427108437502 40.442085129687484 0.000010000001099, -80.0838896046875 40.44156683906249 0.000010000001099, -80.08352620937501 40.44101558906249 0.000010000001099, -80.08315943281252 40.440601884374985 0.000010000001099, -80.08233859375002 40.4399709015625 0.000010000001099, -80.08233178593753 40.43996901718748 0, -80.08233937656252 40.43996354687499 0.000070000007694, -80.08214148125 40.439859453124996 0.000130000014289, -80.08111397343754 40.4396114 0.000130000014289, -80.0801251265625 40.43937412968751 0.000130000014289, -80.07910278906252 40.439014509375 0.000130000014289, -80.07858929375004 40.438555162499995 0.000130000014289, -80.07806963593754 40.437917004687506 0.000130000014289, -80.07770971406251 40.437242078124996 0.000130000014289, -80.07725822187501 40.43642599218748 749.3733023651686, -80.07718769062501 40.43632302968746 749.427112371083, -80.07712874687502 40.43624257187497 749.9474524282746, -80.07703359375 40.43612635937501 749.7023724013374, -80.07694353750003 40.4359844828125 749.7210724033928, -80.07678050312501 40.435733975 750.3598524736024, -80.07663672187499 40.43554447343746 750.4497424834824, -80.07657826875004 40.43546776562499 750.1656224522542, -80.07649563125 40.435364312499985 749.9723824310147, -80.07643754374999 40.4352776515625 750.2220524584565, -80.07636485156252 40.43515753906246 750.0216024364246, -80.07620788593749 40.434926985937466 749.6616923968661, -80.07614522031253 40.43482661718747 749.8936424223602, -80.07603890625 40.434513996874955 749.4986323789439, -80.07601760312502 40.43437722968747 749.8030924124078, -80.07600218281254 40.43422444999999 750.7591325174881, -80.07598848437505 40.434032253125 750.9845225422612, -80.07597532656251 40.433869275 750.9369525370327, -80.07596880156251 40.43355190156251 751.5747426071334, -80.07600302656249 40.433433659375 751.8329426355127, -80.07602437656254 40.43335677812496 751.8949526423283, -80.07611070312504 40.433146904687476 752.5317627123216, -80.07616043125 40.43304884062496 752.7633927377805, -80.07626981562504 40.432764001562475 752.4789427065159, -80.07630192656251 40.43268957968746 752.578022717406, -80.07635092968752 40.43258778124999 752.4339927015754, -80.07638763906255 40.43248764687496 752.3526326926329, -80.07647597031252 40.432232784375 750.1948224554636, -80.0764910546875 40.432195431249966 750.2302624593589, -80.07652444375003 40.432115282812504 750.661362506742, -80.07657478906253 40.43207004687497 751.17448256314, -80.07686845 40.43191312343748 751.5074825997408, -80.07694838125002 40.43188819531247 751.8939726422207, -80.07708502500003 40.43187219062497 752.5701527165411, -80.07722596718753 40.431881592187494 753.3870728063304, -80.07744138125003 40.431916575 753.7358328446634, -80.0775504734375 40.43194261562496 754.0744128818774, -80.07765914062503 40.43196424218746 754.2190928977794, -80.07779621093749 40.43199008281249 754.1616828914694, -80.07792926718753 40.43202195624997 753.8198228538948, -80.07804443437504 40.432044710937475 753.6082028306353, -80.07814736875002 40.432060467187455 753.1866127842974, -80.07829221406251 40.43208079062498 752.6895727296667, -80.07840533125 40.432092574999956 752.1826826739534, -80.0785204671875 40.432101864062474 751.8391826361986, -80.07861190624999 40.43210570312499 751.7168026227475, -80.07870719531252 40.432109620312474 751.4769725963873, -80.07881838437504 40.43211012031247 751.532422602482, -80.0789227203125 40.43211296718749 751.4599125945123, -80.07903423281249 40.432123967187465 375.8733913130214, -80.07938808125004 40.43216728906248 0.000130000014289, -80.080000934375 40.43222283749998 0.000130000014289, -80.08035073593754 40.432220026562504 0.000130000014289, -80.08038902343753 40.43222130468746 0.000070000007694, -80.08037625781253 40.432184657812456 0, -80.0803755453125 40.43216404062497 0, -80.08260655625003 40.43144854999997 0.000010000001099, -80.08370363124999 40.430983124999955 0.000010000001099, -80.08448488125003 40.43056756562498 0.000010000001099, -80.0851331515625 40.43008551874999 0.000010000001099, -80.08591440156249 40.42923777968747 0.000010000001099, -80.086329959375 40.42855626406248 0.000010000001099, -80.08654605000004 40.4281074609375 0.000010000001099, -80.08646293906253 40.42624575937498 0.000010000001099, -80.0861120125 40.423774014062474 0.000010000001099, -80.0853824875 40.42149177031246 0.000010000001099, -80.08505004062499 40.420909989062466 0.000010000001099, -80.084368525 40.420161984375 0.000010000001099, -80.08350416249999 40.41976304843746 0.000010000001099, -80.08145961562502 40.419962515625 0.000010000001099, -80.08057863125003 40.42006225 0.000010000001099, -80.07961453593754 40.41994589374997 0.000010000001099, -80.07853873593751 40.42003944218749 0.000010000001099, -80.07509204531254 40.420736964062485 0.000010000001099, -80.07522950781254 40.41927900781246 0.000010000001099, -80.07619643437499 40.4176683 0.000010000001099, -80.07943778125002 40.41627417968749 0.000010000001099, -80.07963266249999 40.41495059531246 0.000010000001099, -80.07938088437504 40.414468229687486 0.000010000001099, -80.07911338125001 40.41424960312497 0.000010000001099, -80.07939951562503 40.413396535937466 0.000010000001099, -80.07948820625 40.41337988906247 0.000010000001099, -80.08040270625003 40.412987584375 0.000010000001099, -80.08053647343752 40.4129833140625 0.000010000001099, -80.08310012343753 40.41236682343748 0.000010000001099, -80.0831120640625 40.41236521874998 0.000010000001099, -80.08403064375 40.41194931093747 0.000010000001099, -80.08475409062504 40.411719521875 0.000010000001099, -80.085951840625 40.411126254687474 0.000010000001099, -80.08753316875004 40.41029807812498 0.000010000001099, -80.08753890000003 40.410305770312505 0.000010000001099, -80.08803529375001 40.41003388125 0.000010000001099, -80.08836825000003 40.409773884375 0.000010000001099, -80.08862164062504 40.409480881249976 0.000010000001099, -80.08865744531249 40.409268907812475 0.000010000001099, -80.08861606406253 40.40884766562499 0.000010000001099, -80.08852657187504 40.40782643437501 0.000010000001099, -80.08932340625 40.40801669374997 0.000010000001099, -80.08889356093749 40.40886064531247 0.000010000001099, -80.08881133125004 40.40937444999997 0.000010000001099, -80.08868048750003 40.40965402968749 0.000010000001099, -80.08845625468751 40.40987890781247 0.000010000001099, -80.0879997796875 40.41022427343751 0.000010000001099, -80.08762493593753 40.410421231249984 0.000010000001099, -80.08762828125003 40.41042572187496 0.000010000001099, -80.08604666406251 40.411275046875005 0.000010000001099, -80.08491700156253 40.41194816093747 0.000010000001099, -80.08431231093749 40.4121691265625 0.000010000001099, -80.083542959375 40.412574067187506 0.000010000001099, -80.08320299843751 40.41285889531247 0.000010000001099, -80.08072310624999 40.413128973437495 0.000010000001099, -80.08066220937502 40.413148290624974 0.000010000001099, -80.0801617796875 40.4134201 0.000010000001099, -80.07981372187504 40.41381371718751 0.000010000001099, -80.08011095781251 40.4150009234375 0.000010000001099, -80.08013187187504 40.415014989062456 0.000010000001099, -80.080243784375 40.416239 0.000010000001099, -80.07690326875002 40.41803230312496 0.000010000001099, -80.07672900312502 40.419497974999956 0.000010000001099, -80.07775283437502 40.41976304843746 0.000010000001099, -80.07823488281252 40.41982953749999 0.000010000001099, -80.07829679375004 40.41982957968747 0.000010000001099, -80.07832825625002 40.419820590624965 0.000010000001099, -80.07846759531253 40.419779670312494 0.000010000001099, -80.07993036093751 40.41987940468749 0.000010000001099, -80.080761478125 40.41989602656247 0.000010000001099, -80.08119365781249 40.41986278125 0.000010000001099, -80.08215775312505 40.41969655781247 0.000010000001099, -80.08350416249999 40.419546957812486 0.000010000001099, -80.08445163593751 40.41989602656247 0.000010000001099, -80.08511652968753 40.42067727656246 0.000010000001099, -80.0856152 40.42139203749997 0.000010000001099, -80.08623022656252 40.42355294062497 0.000010000001099, -80.08666240625001 40.425497753125 0.000010000001099, -80.08681200781251 40.427442567187484 0.000010000001099, -80.0866790296875 40.42817394999997 0.000010000001099, -80.08644631562504 40.428805598437464 0.000010000001099, -80.08598089062502 40.42950373593749 0.000010000001099, -80.08514977343754 40.430334853124975 0.000010000001099, -80.0833545625 40.43139868281247 0.000010000001099, -80.08058637812502 40.43232809687498 0.000130000014289, -80.08052368437501 40.432403274999956 0.000130000014289, -80.08046149531253 40.4326931234375 0.000130000014289, -80.08032044687502 40.433111884374966 0.000130000014289, -80.0802271515625 40.433466020312494 0.000130000014289, -80.08025508281253 40.43379224687499 0.000130000014289, -80.080286365625 40.434054745312494 0.000130000014289, -80.08050106249999 40.4345801140625 0.000130000014289, -80.08152547343752 40.43669545156246 0.000130000014289, -80.08252813281251 40.438856798437484 0.000130000014289, -80.0831498078125 40.44007355937498 0.000130000014289, -80.08308792343752 40.440076562499996 0.000130000014289, -80.0833011265625 40.44031780468748 0.000010000001099, -80.083762009375 40.44089256874997 0.000010000001099, -80.08421452812502 40.441488875 0.000010000001099, -80.08469449687504 40.4421471375 0.000010000001099, -80.08612965156254 40.4432187765625 0.000010000001099, -80.08925789687504 40.44654878124999 0.000010000001099, -80.08998147187503 40.44849556718748 0.000010000001099, -80.09008006093751 40.44865951093749 0.000010000001099, -80.09077404843754 40.44890363437497 0.000010000001099, -80.09148720937503 40.44832762812496 0.000010000001099, -80.09311214531249 40.45005706874997 0.000010000001099, -80.09176970312501 40.45101454999997 0.000010000001099, -80.089941828125 40.45093583124998 0.000010000001099))
        """)

        with open('/usr/data/jumbo_leveed_area.wkt') as j:
            geom_jumbo = wkt.loads(j.read())

        pa_dem = '/usr/data/pa_512.tif'
        miss_dem = '/usr/data/miss.tif'

        geom = geo_utils.reproject(geom_pitts, 'epsg:4269', 'epsg:4326')
        geoprocessing.elevation_increments(geom, pa_dem)


class WeightedOverlayTests(unittest.TestCase):
    def test_weighted_overlay(self):
        """
        Tests that rasters are appropriately weighted and summed
        for the weighted overlay operation
        """
        geom = Polygon([
            [1747032.24039185303263366, 2071990.49254682078026235],
            [1747037.83687203959561884, 2071660.30021581239998341],
            [1747416.29884465713985264, 2071660.99977583577856421],
            [1747415.59928463399410248, 2071989.79298679763451219],
            [1747032.24039185303263366, 2071990.49254682078026235]
        ])

        rasters = [NLCD_ONES, NLCD_THREES]
        weights = [   0.75  ,    0.25    ]  # noqa

        # Raster with all 1 values overlayed with all 3 values and their
        # weights should produce a new layer with all cells having the
        # value of `expected`
        expected = 1 * weights[0] + 3 * weights[1]
        layer = geoprocessing.weighted_overlay(geom, rasters, weights)
        self.assertTrue(np.all(layer == expected))


class RelassificationTests(unittest.TestCase):
    reclass_geom = Polygon([
        [1747032.24039185303263366, 2071990.49254682078026235],
        [1747037.83687203959561884, 2071660.30021581239998341],
        [1747416.29884465713985264, 2071660.99977583577856421],
        [1747415.59928463399410248, 2071989.79298679763451219],
        [1747032.24039185303263366, 2071990.49254682078026235]
    ])

    def test_single_reclass(self):
        """
        Tests that a single substitution is made for a reclass definition
        """
        reclass = [(11, 100)]
        new_layer = geoprocessing.reclassify(self.reclass_geom,
                                             NLCD_PATH, reclass)
        self.assertFalse(np.any(new_layer == 11))

        orig_count = geoprocessing.count(self.reclass_geom, NLCD_PATH)[1]['11']
        new_count = geoprocessing.masked_array_count(new_layer)[1]['100']

        self.assertEqual(orig_count, new_count)

    def test_multi_reclass(self):
        """
        Tests that a multiple substitutions are made for a reclass definition
        containing more than one definition
        """
        reclass = [(11, 100), (21, 200)]
        new_layer = geoprocessing.reclassify(self.reclass_geom, NLCD_PATH,
                                             reclass)
        self.assertFalse(np.any(new_layer == 11))
        self.assertFalse(np.any(new_layer == 21))

        orig_counts = geoprocessing.count(self.reclass_geom, NLCD_PATH)[1]
        new_counts = geoprocessing.masked_array_count(new_layer)[1]

        self.assertEqual(orig_counts['11'], new_counts['100'])
        self.assertEqual(orig_counts['21'], new_counts['200'])

    def test_range_reclass(self):
        """
        Tests a single reclass definition representing a range of values
        to reclass to the same value
        """
        reclass = [((22, 24), 200)]
        new_layer = geoprocessing.reclassify(self.reclass_geom,
                                             NLCD_PATH, reclass)

        # An inclusive range of values, present in the test data, should not
        # exist after reclassification
        self.assertFalse(np.any(new_layer == 22))
        self.assertFalse(np.any(new_layer == 23))
        self.assertFalse(np.any(new_layer == 24))

        orig_counts = geoprocessing.count(self.reclass_geom, NLCD_PATH)[1]
        old_count = orig_counts['22'] + orig_counts['23'] + orig_counts['24']

        new_count = geoprocessing.masked_array_count(new_layer)[1]['200']

        self.assertEqual(old_count, new_count)


class StatisticsTests(unittest.TestCase):
    """
    The statistics method is a shim over direct numpy methods and
    is therefore not extensively tested.  These tests should ensure
    that the method is proxying the right calls and generally working
    """
    stats_geom = Polygon([
            [1747260.99651947943493724, 2071928.23170474520884454],
            [1747260.99651947943493724, 2071884.15942327585071325],
            [1747323.9569215786177665, 2071882.06074320594780147],
            [1747321.85824150871485472, 2071927.53214472183026373],
            [1747260.99651947943493724, 2071928.23170474520884454]])

    geom_data = [11, 23, 24]

    def test_mean(self):
        """
        Test that the statitistics method returns the right value for mean
        """
        mean = geoprocessing.statistics(self.stats_geom, NLCD_PATH, 'mean')
        self.assertEqual(mean, sum(self.geom_data)/len(self.geom_data))

    def test_min(self):
        """
        Test that the statitistics method returns the right value for min
        """
        min_val = geoprocessing.statistics(self.stats_geom, NLCD_PATH, 'min')
        self.assertEqual(min_val, min(self.geom_data))

    def test_not_implmented(self):
        """
        Tests that unimplemented stats operations raise
        """
        self.assertRaises(Exception, geoprocessing.statistics,
                          self.stats_geom, NLCD_PATH, 'foo')


class ImageTests(unittest.TestCase):
    def test_decimated_read(self):
        """
        Test that a bounding box of greater than 256x256 is decimated to that
        shape on read
        """
        tile_src = box(1582986.11448, 2088466.53022,
                       1611281.91831, 2062319.77478)
        tile, _ = geo_utils.tile_read(tile_src, NLCD_LARGE)
        self.assertEqual(tile.shape, (256, 256))

    def test_color_palette(self):
        """
        Test that a raster source ColorTable is converted to an RGB array
        """
        colormap = {
            0: (100, 100, 100, 255),
            99: (45, 45, 45, 255),
            255: (75, 75, 75, 255)
        }

        class mock_reader():
            def colormap(self, _):
                return colormap

        palette = geo_utils.color_table_to_palette(mock_reader())

        # Test the the indexs of the palette match value + 3 (R,G & B)
        self.assertItemsEqual(palette[0:3], colormap[0][0:3])
        self.assertItemsEqual(palette[297:300], colormap[99][0:3])
        self.assertItemsEqual(palette[765:768], colormap[255][0:3])


class S3Tests(unittest.TestCase):
    def setUp(self):
        self.url = 's3://simple-raster-processing/nlcd_512_lzw_tiled.tif'
        self.geom = Polygon([
            [1747260.99651947943493724, 2071928.23170474520884454],
            [1747260.99651947943493724, 2071884.15942327585071325],
            [1747323.9569215786177665, 2071882.06074320594780147],
            [1747321.85824150871485472, 2071927.53214472183026373],
            [1747260.99651947943493724, 2071928.23170474520884454]])


    def test_read_count(self):
        """Test a small byte offset raster read using vsicurl s3 url"""

        _, s3_counts = geoprocessing.count(self.geom, self.url)
        _, disk_counts = geoprocessing.count(self.geom, NLCD_PATH)

        self.assertDictEqual(s3_counts, disk_counts,
                             "Reading the same offset from a local and s3 " +
                             "file did not produce equivalent results")


if __name__ == '__main__':
    unittest.main()
