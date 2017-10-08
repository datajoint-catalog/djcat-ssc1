#! /usr/bin/env python

import os

import re
import code
from decimal import Decimal
from importlib import reload

from datetime import datetime

from nwb import nwb_file
from nwb import nwb_utils

import h5py

from pymysql.err import IntegrityError

import yaml

import datajoint as dj

{'unused': [code, nwb_utils, IntegrityError, yaml, Decimal, re]}
# 23456789_123456789_123456789_123456789_123456789_123456789_123456789_12345678

dj.config['database.host'] = 'localhost'
dj.config['database.user'] = 'chris'
dj.config['database.password'] = ''
dj.config['names.djcat_lab'] = 'tutorial_lab'
dj.config['names.ssc1'] = 'tutorial_ssc1_ingest'

dj.config['display.limit'] = 5
dj.config['safemode'] = False


nwbfiledir = 'data'

# data drop fun & games

schema = dj.schema(dj.config['names.ssc1'], locals())
schema.drop(force=True)
schema = dj.schema(dj.config['names.ssc1'], locals())

import djcat_lab as lab
lab.schema.drop(force=True)  # XXX! dangerous - lab may reference other schema
reload(lab)


def open_nwb(fname):
    use_nwb_file = False  # slower due to validation; more memory use
    if use_nwb_file:
        return nwb_file.open(fname, None, 'r').file_pointer
    else:
        return h5py.File(fname, 'r')


def study_from_nwb(fh):
    key = {}
    g_gen = fh['general']

    key['study'] = 'ssc1'
    key['study_description'] = fh['session_description'][()].decode()
    key['institution'] = g_gen['institution'][()].decode()
    key['lab'] = g_gen['lab'][()].decode()
    key['reference_atlas'] = ''  # XXX: not in file

    lab.Lab().insert1(key, ignore_extra_fields=True)
    lab.Study().insert1(key, ignore_extra_fields=True)


@schema
class InputFile(dj.Lookup):
    definition = '''
    nwb_file: varchar(255)
    '''

    contents = [[os.path.join(nwbfiledir, f)]
                for f in os.listdir(nwbfiledir) if f.endswith('.nwb')]


@schema
class Session(dj.Imported):

    definition = """
    -> lab.Subject
    session_id		: bigint	# YYYYMMDD digits
    ---
    -> lab.Study
    session_date	: date		# session date
    experimenter	: varchar(60)	# experimenter's name
    session_start_time	: datetime
    -> InputFile
    """

    @property
    def key_source(self):
        return InputFile()

    def _make_tuples(self, key):

        fname = key['nwb_file']  # YYYYMMDD_RN.nwb
        print('Session()._make_tuples: nwb_file', key['nwb_file'])

        f = open_nwb(fname)

        #
        # General Study Information (in all files - only load 1x)
        #

        key['study'] = 'ssc1'
        try:
            study_from_nwb(f)
        except IntegrityError as e:
            if 'Duplicate entry' in e.args[1]:
                pass
            else:
                raise

        #
        # General Session Information
        #

        g_gen = f['general']
        g_subj = f['general']['subject']

        s_str = g_gen['session_id'][()].decode()

        key['session_id'] = str.join('', s_str.split('_')[1:4])  # YYYYMMDD
        key['experimenter'] = g_gen['experimenter'][()].decode()

        stime = f['session_start_time'][()].decode()
        sdate = datetime.strptime(stime, '%a %b %d %Y %H:%M:%S')

        key['session_start_time'] = sdate
        key['session_date'] = sdate.date()

        #
        # Subject
        #

        key['subject_id'] = g_gen['subject']['subject_id'][()].decode()[2:]

        if not (lab.Subject() & key):

            key['species'] = g_subj['species'][()].decode()
            key['date_of_birth'] = '1970-01-01'
            key['sex'] = str.upper(g_subj['sex'][()].decode())

            try:
                lab.Subject().insert1(key, ignore_extra_fields=True)
            except:
                print('subject insert error')
                print(yaml.dump(key))
                raise

            '''
            # TODO: needs parsing
            >>> print(hdf_str(g_subj['description']))
            animalStrain1: 006528; animalStrain2: 023139;
            animalSource1: JAX; animalSource2: JAX
            '''
            # key['animal_source'] = ''
            # key['source_name'] = g_subj['description']
            # lab.SubjectSource().insert1(key, ignore_extra_fields=True)
            # lab.Subject.Source().insert1(key, ignore_extra_fields=True)

            # key['strain_id'] = g_subj['description']
            # lab.StrainType().insert1(key, ignore_extra_fields=True)
            # lab.Subject.Strain().insert1(key, ignore_extra_fields=True)

        Session().insert1(key, ignore_extra_fields=True)


if __name__ == '__main__':
    Session().populate()
    print('import complete.')
