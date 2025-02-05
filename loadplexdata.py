#!/usr/bin/env python3
# copyright 2017 Brian Khoyi
#
#
#
#
#

import os
import errno
import platform
import time
import shutil
import smtplib
import argparse
import logging
import subprocess
import multiprocessing
import queue
import hashlib
import tarfile
import configparser
import sys
import yaml
import re


class Plex_Lib_Manager(object):
    """
    This manages Movie and TV collections for Plex
    The fist objective is to load, verify, and correct plex libraries with content generated by MakeMKV
    """

    def __init__(self, input_path, output_path, convert_list_path="/etc/"):
        """
        Loads in the conversion list.
        :param input_path:
        :param output_path:
        :param convert_list_path:
        """
        self.input_path = input_path
        self.output_path = output_path

        with open(convert_list_path, 'r') as s:
            try:
                self.conversion_dict = yaml.load(s)
            except yaml.YAMLError as e:
                raise e
        # print( self.conversion_dict)

    def detect_missing_dictionary_entries(self):
        """
        copies the directories with only listed exceptions.  not 100% safe...
        :return:
        """
        if "DVR_Shows" in self.conversion_dict.keys():
            #print( self.conversion_dict['DVR_Shows'])
            for show_name in sorted(os.listdir(self.input_path)):
                #print( show_name)
                try:
                    for e in sorted(self.conversion_dict['DVR_Shows']['exceptions'].keys()):
                        #print( self.conversion_dict['DVR_Shows']['exceptions'][e])
                        if self.conversion_dict['DVR_Shows']['exceptions'][e] in show_name:
                            #print (e, show_name)
                            raise NameError(show_name)
                    for root, subFolders, files in sorted(os.walk(os.path.join(self.input_path, show_name))):
                        for filename in sorted(set(files)):
                            filePath = os.path.join(root, filename)
                            dest_dir = root.replace( self.input_path, self.output_path)
                            # filter out ' Season ##' postfixes to titles
                            title = str( dest_dir).split( '/')[-2]
                            title = title.split('Season')[0].split('season')[0].split('_ The Complete')[0].rstrip(' ')
                            dest_dir = dest_dir.replace(str( dest_dir).split( '/')[-2], title)
                            # filter out ' ####' postfixes to titles
                            title = str( dest_dir).split( '/')[-2]
                            r = re.compile('[0-9]{4}')
                            temp = str( r.sub('', title))
                            if temp in title:
                                if temp.__len__() is not title.__len__():
                                    dest_dir = dest_dir.replace(title, temp.rstrip(' '))
                            #print( dest_dir )
                            #self.copy_file(source_fullpath=filePath, dest_dir=dest_dir, dest_name=filename)
                except NameError as e:
                    print( '{} is being skipped'.format(e))

    def DVR_TV_copy(self):
        """
        copies the directories with only listed exceptions.  not 100% safe...
        :return:
        """
        if "DVR_Shows" in self.conversion_dict.keys():
            #print( self.conversion_dict['DVR_Shows'])
            for show_name in sorted(os.listdir(self.input_path)):
                #print( show_name)
                try:
                    for e in sorted(self.conversion_dict['DVR_Shows']['exceptions'].keys()):
                        #print( self.conversion_dict['DVR_Shows']['exceptions'][e])
                        if self.conversion_dict['DVR_Shows']['exceptions'][e] in show_name:
                            #print (e, show_name)
                            raise NameError(show_name)
                    for root, subFolders, files in sorted(os.walk(os.path.join(self.input_path, show_name))):
                        for filename in sorted(set(files)):
                            filePath = os.path.join(root, filename)
                            dest_dir = root.replace( self.input_path, self.output_path)
                            # filter out ' Season ##' postfixes to titles
                            title = str( dest_dir).split( '/')[-2]
                            title = title.split('Season')[0].split('season')[0].split('_ The Complete')[0].rstrip(' ')
                            filename = filename.replace(str( dest_dir).split( '/')[-2], title)
                            dest_dir = dest_dir.replace(str( dest_dir).split( '/')[-2], title)
                            # filter out ' ####' postfixes to titles
                            title = str( dest_dir).split( '/')[-2]
                            r = re.compile('[0-9]{4}')
                            temp = str( r.sub('', title))
                            if temp in title:
                                if temp.__len__() is not title.__len__():
                                    dest_dir = dest_dir.replace(title, temp.rstrip(' '))
                                    filename = filename.replace(title, temp.rstrip(' '))
                            #print( dest_dir )
                            self.copy_file(source_fullpath=filePath, dest_dir=dest_dir, dest_name=filename)
                except NameError as e:
                    print( '{} is being skipped'.format(e))

    def DVR_Movies_copy(self):
        """
        copies the directories with only listed exceptions.  not 100% safe...
        :return:
        """
        if "DVR_Movies" in self.conversion_dict.keys():
            # print( self.conversion_dict['DVR_Movies'])
            for e in sorted(self.conversion_dict['DVR_Movies']['feeds'].keys()):
                # print( self.conversion_dict['DVR_Movies']['feeds'][e])
                for movie_name in sorted(os.listdir(os.path.join( self.input_path, self.conversion_dict['DVR_Movies']['feeds'][e]))):
                    #print( movie_name)
                    source = os.path.join( os.path.join( self.input_path, self.conversion_dict['DVR_Movies']['feeds'][e]), movie_name)
                    movie_dest = os.path.join( self.output_path, movie_name.split('.')[0])
                    ## TODO:  filter the files against the yaml list
                    self.copy_file(source_fullpath=source, dest_dir=movie_dest, dest_name=movie_name)

    def safe_load(self):
        """
        Safely Loads files, no overwriting.
        :return:
        """
        if "TV" in self.conversion_dict.keys():
            # print( self.conversion_dict['TV'])
            for show in sorted(self.conversion_dict['TV'].keys()):
                for season in sorted(self.conversion_dict['TV'][show].keys()):
                    for episode in sorted(self.conversion_dict['TV'][show][season].keys()):
                        episode_dict = self.conversion_dict['TV'][show][season][episode]
                        episode_name = "{} - S{}E{} - {}.mkv".format(show, season, episode, episode_dict["title"])
                        source_dir = episode_dict["source_dir"]
                        source_name = episode_dict["source_name"]
                        dest_dir = os.path.join(self.output_path, show, "Season {}".format(season))
                        try:
                            for d in os.listdir(self.input_path):
                                if source_dir.replace('-', '').replace(' ', '_') in d.replace('-', '').replace(' ', '_'):
                                    source_dir = d
                        except:
                            #print(os.path.join(self.input_path, source_dir))
                            source_dir = source_dir
                        try:
                            for f in os.listdir(os.path.join(self.input_path, source_dir)):
                                if source_name.replace('-', '').replace(' ', '_') in f.replace('-', '').replace(' ', '_'):
                                    source_name = f
                        except:
                            #print(os.path.join(self.input_path, source_dir))
                            source_name = source_name
                        source = os.path.join(self.input_path, source_dir, source_name)
                        #dest_fullpath = os.path.join(dest_dir, episode_name)
                        self.copy_file(source_fullpath=source, dest_dir=dest_dir, dest_name=episode_name)

        if "Movies" in self.conversion_dict.keys():
            # print( self.conversion_dict['Movies'])
            for movie in sorted(self.conversion_dict['Movies'].keys()):
                dest_dir = os.path.join(self.output_path, movie)

                for edition in self.conversion_dict['Movies'][movie]["Feature"].keys():
                    edition_dict = self.conversion_dict['Movies'][movie]["Feature"][edition]
                    dest_name = "{} - {}.mkv".format(movie, edition_dict["edition"])
                    source_dir = edition_dict["source_dir"]
                    source_name = edition_dict["source_name"]
                    # look up source_dir and use a close enough match
                    try:
                        for d in os.listdir(self.input_path):
                            if source_dir.replace('-', '').replace(' ', '_') == d.replace('-', '').replace(' ', '_'):
                                source_dir = d
                    except:
                        #print(os.path.join(self.input_path, edition_dict["source_dir"]))
                        source_dir = source_dir
                    # look up filename based on if supplied title in the name of a file in the supplied directory
                    try:
                        for f in os.listdir(os.path.join(self.input_path, source_dir)):
                            if source_name.replace('-', '').replace(' ', '_') in f.replace('-', '').replace(' ', '_'):
                                source_name = f
                    except:
                        #print(os.path.join(self.input_path, source_dir))
                        source_dir = source_dir
                    source = os.path.join(self.input_path, source_dir, source_name)
                    self.copy_file(source_fullpath=source, dest_dir=dest_dir, dest_name=dest_name)

                if "Bonus" in self.conversion_dict['Movies'][movie].keys():
                  for bonus in self.conversion_dict['Movies'][movie]["Bonus"].keys():
                    bonus_dict = self.conversion_dict['Movies'][movie]["Bonus"][bonus]
                    dest_name = "{}-{}.mkv".format(bonus, bonus_dict["type"])
                    source = os.path.join(self.input_path, bonus_dict["source_dir"], bonus_dict["source_name"])
                    # look up filename based on if supplied title in the name of a file in the supplied directory
                    try:
                        for f in os.listdir(os.path.join(self.input_path, bonus_dict["source_dir"])):
                            if bonus_dict["source_name"] in f:
                                source = os.path.join(self.input_path, bonus_dict["source_dir"], f)
                    except:
                        #print(os.path.join(self.input_path, bonus_dict["source_dir"]))
                        source = source
                    self.copy_file(source_fullpath=source, dest_dir=dest_dir, dest_name=dest_name)

                ## TODO:  upload any .mkv files in listed directories as bonus content, to avoid needing to generate per file entries

    def copy_file(self, source_fullpath, dest_dir, dest_name):
        """
        This function copies the the requested file, printing out the results
        :param source_full:
        :param dest_path:
        :param dest_name:
        :return:
        """
        dest_fullpath = os.path.join(dest_dir, dest_name)
        if os.path.exists(source_fullpath):
            if not os.path.exists(dest_fullpath):
                print("Link \"{}\" to \"{}\"".format(source_fullpath, dest_fullpath))
                self.mkdir_p(dest_dir)
                # shutil.copy2(source_fullpath, dest_fullpath)
                os.symlink(source_fullpath, dest_fullpath)
            else:
                #print("{} Exists Already!".format(dest_fullpath))
                source_fullpath="Done"
        else:
            #print("{}\" does not exist!".format(source_fullpath))
            return True

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def make_writable_tree(self, path):
        """
        This function makes all of the files and folders writable in the given tree.
        """
        logging.debug(("Trying to fix permissions for folder " + path))
        for root, subFolders, files in os.walk(path):
            for folder in subFolders:
                # logging.debug((os.path.join(root, folder)))
                os.chmod(os.path.join(root, folder), 0o775)
            for filename in files:
                # logging.debug((os.path.join(root, filename)))
                os.chmod(os.path.join(root, filename), 0o664)

    def list_files_in_tree(self, path, return_queue):
        """
        This function will find the files in the provided path's tree.
        :param path:
        :param return_queue:
        :return :
        """
        ## TODO:  consider using recursive threads instead of walk
        for root, subFolders, files in os.walk(path):
            for filename in set(files):
                filePath = os.path.join(root, filename)
                return_queue.put(filePath, block=True)

    def return_file_checksum(self, filePath, hash="sha512", blocksize=65536):
        """
        This function reads the file and calculates the sha512 checksum
        :param filePath:
        :param hash:
        :param blocksize:
        :return sha512:
        """
        ## TODO:  consider using settigns for defaults
        hasher = hashlib.new(hash)
        with open(filePath, 'rb') as file:
            buffer = file.read(blocksize)
            while len(buffer) > 0:
                hasher.update(buffer)
                buffer = file.read(blocksize)
        return hasher.hexdigest()


def rm_rf(path):
    """
    This function is used because shutil.rmtree fails to remove read-only files.
    """
    if os.path.isdir(path):
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for f in files:
                    os.chmod(os.path.join(root, f), 0o666)
                    os.remove(os.path.join(root, f))
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o666)
            shutil.rmtree(path)
        except:
            logging.error(("couldn't remove files/folders in " + path))
    else:
        try:
            os.chmod(path, 0o666)
            os.remove(path)
        except:
            logging.error(("Was there ever a file in " + path + "?"))
    output = "couldn't run rm -rf " + path
    try:
        output = subprocess.check_output(("rm -rf " + path), shell=True)
    except:
        logging.error(("couldn't run rm -rf at path:  " + path))
    return output


def archive_extractor(archive_name, archive_root):
    """
    This function extracts archive_name to archive_root.
    depends on tarfile
    :param archive_name:
    :param archive_root:
    :return:
    """
    with tarfile.open(archive_name, "r") as archive:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(archive, archive_root)


def archive_loader(archive_name, archive_root, input_queue, done_adding_to_queue):
    """
    This function does the work of archiving files.
        It creates the archive file
        waits a minute (to avoid blocking other processes)
        begins archiving as files are added to the queue
    This function will not close until the queue is empty AND done_adding_to_queue is set
    depends on multiprocessing, queue, and tarfile
    :param archive_name:
    :param archive_root:
    :param input_queue:
    :param done_adding_to_queue:
    :return:
    """
    with tarfile.open(archive_name, "w:xz", compresslevel="9e") as archive:
        while not done_adding_to_queue.is_set():
            try:
                filePath = input_queue.get(block=True, timeout=60)
            except queue.Empty:
                pass
            else:
                ## TODO:  verify that it works!
                archive.add(filePath, filePath.lstrip(archive_root))
                input_queue.task_done()


def hr_size(num):
    """ Helper function """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if num < 1024.0:
            return "{} {}".format('{0:.1f}'.format(num), x)
        num /= 1024.0
    return "{} {}".format('{0:.1f}'.format(num), 'YB')


def parse_arguments():
    """

    :return:
    """
    parser = argparse.ArgumentParser(description='TODO',
                                     epilog='if you are reading this, email Brian.Khoyi@gmail.com')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help='changes logging to debug for this run of the command')
    parser.add_argument('--dvr',
                        action="store_true",
                        help='copies structure from a compatible DVR largely as-is, using only an exemption table to filter')
    parser.add_argument('--report',
                        action="store_true",
                        help='report on files that do not have conversion rules')
    parser.add_argument('-i', '--inputpath',
                        type=str,
                        help="""TODO""")
    parser.add_argument('-o', '--outputpath',
                        type=str,
                        help="""TODO""")
    parser.add_argument('-c', '--conversionrules',
                        type=str,
                        help='TODO')
    return parser.parse_args()


def main():
    time.sleep(1)
    print( "First line of output test")
    time.sleep(1)
    print( "Second line of output test")
    time.sleep(1)
    print( "Third line of output test")
    time.sleep(1)
    print( "Fourth line of output test")
    # startup logger and managed_dir control of the cache
    args = parse_arguments()
    # Setting logger's verbosity now.  Creating log file if needed.
    if args.verbose:
        logging.basicConfig(filename="./loadplexdata.log", level=logging.DEBUG)
    else:
        logging.basicConfig(filename="./loadplexdata.log", level=logging.INFO)
    logging.debug('Running with Python version {}.{}.{} {} {}'.format(sys.version_info.major, sys.version_info.minor,
                                                                      sys.version_info.micro,
                                                                      sys.version_info.releaselevel,
                                                                      sys.version_info.serial))

    plexlib = Plex_Lib_Manager(args.inputpath, args.outputpath, args.conversionrules)
    if args.dvr:
        if 'TV' in args.conversionrules:
            plexlib.DVR_TV_copy()
        else:
            plexlib.DVR_Movies_copy()
    elif args.report:
        plexlib.detect_missing_dictionary_entries()
    else:
        plexlib.safe_load()


main()



"""
    "00":
      "10":
        title: "Featurette with Cast and Crew"
        source_dir: "SG1_V2"
        source_name: "title05.mkv"
      "11":
        title: "Promotional trailers S01D02"
        source_dir: "SG1_V2"
        source_name: "title06.mkv"
      "12":
        title: "Profile on General Hammond Featurette"
        source_dir: "SG1_V3"
        source_name: "title05.mkv"
      "13":
        title: "Profile on Captain Carter Featurette"
        source_dir: "SG1_V4"
        source_name: "title05.mkv"
      "14":
        title: "Behind the Scenes with the Producers of Stargate SG-1 (clips from Seasons 1-4)"
        source_dir: "SG1_V4"
        source_name: "title06.mkv"
      "15":
        title: "Stargate SG-1 Costume Design Featurette"
        source_dir: "SG1_V5"
        source_name: "title03.mkv"
      "16":
        title: "Production Design Featurette"
        source_dir: "SG1_V1_R1_YR2"
        source_name: "title04.mkv"
      "17":
        title: "Profile on Dr. Jackson"
        source_dir: "SG1_V4_R1_YR2"
        source_name: "title04.mkv"
      "18":
        title: "Profile on Teal_c"
        source_dir: "SG1_V5_R1_YR2"
        source_name: "title04.mkv"
      "19":
        title: "Secret Files of the SGC—Colonel Jack O'Neill"
        source_dir: "SG1_V1_R1_YR3"
        source_name: "title04.mkv"
      "20":
        title: "Secret Files of the SGC—The Stargate Universe"
        source_dir: "SG1_V3_R1_YR3"
        source_name: "title04.mkv"
      "21":
        title: "Secret Files of the SGC- Personnel Files"
        source_dir: "SG1_V4_R1_YR3"
        source_name: "title04.mkv"
      "22":
        title: "Secret Files of the SGC—Enhanced Visual Effects Featurette"
        source_dir: "SG1_V1_R1_YR4"
        source_name: "title04.mkv"
      "23":
        title: "Secret Files of the SGC—Alien Species- Friend & Foe Featurette"
        source_dir: "SG1_V2_R1_YR4"
        source_name: "title04.mkv"
      "24":
        title: "Stargate SG-1- Timeline to the Future—Legacy of the Gate"
        source_dir: "SG1_V5_R1_YR4"
        source_name: "title04.mkv"
      "25":
        title: "Inside the Tomb Featurette"
        source_dir: "STARGATE_SG1_V2_R1_YR5"
        source_name: "title04.mkv"
      "26":
        title: "SG-1 Video Diary—Amanda Tapping"
        source_dir: "STARGATE_SG1_V2_R1_YR5"
        source_name: "title05.mkv"
      "27":
        title: "SG-1 Video Diary—Christopher Judge"
        source_dir: "STARGATE_SG1_V3_R1_YR5"
        source_name: "title04.mkv"
      "28":
        title: "SG-1 Video Diary—Michael Shanks"
        source_dir: "STARGATE_SG1_V4_R1_YR5"
        source_name: "title05.mkv"
      "29":
        title: "Dr. Daniel Jackson—A Tribute"
        source_dir: "STARGATE_SG1_V5_R1_YR5"
        source_name: "title05.mkv"
      "30":
        title: "Directors Series- Redemption with behind the scenes clips of the making of parts one and two of this episode"
        source_dir: "STARGATE_SG1_V1_R1_YR6"
        source_name: "title04.mkv"
      "31":
        title: "Directors Series- 6.03 Descent with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V1_R1_YR6"
        source_name: "title05.mkv"
      "32":
        title: "Directors Series- Frozen with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V1_R1_YR6"
        source_name: "title06.mkv"
      "33":
        title: "Directors Series- 6.05 Nightwalkers with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR6"
        source_name: "title04.mkv"
      "34":
        title: "Directors Series- 6.06 Abyss with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR6"
        source_name: "title05.mkv"
      "35":
        title: "Directors Series- 6.07 Shadow Play with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR6"
        source_name: "title06.mkv"
      "36":
        title: "Directors Series- 6.08 The Other Guys with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR6"
        source_name: "title07.mkv"
      "37":
        title: "Directors Series- 6.09 Allegiance with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V3_R1_YR6"
        source_name: "title04.mkv"
      "38":
        title: "Directors Series- 6.10 Cure with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V3_R1_YR6"
        source_name: "title05.mkv"
      "39":
        title: "Directors Series- 6.11 Prometheus with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V3_R1_YR6"
        source_name: "title06.mkv"
      "40":
        title: "Directors Series- 6.16 Metamorphosis with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V4_R1_YR6"
        source_name: "title05.mkv"
      "41":
        title: "Directors Series- 6.22 Full Circle with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V5_R1_YR6"
        source_name: "title05.mkv"
      "42":
        title: "SG-1 Beyond the Gate- Michael Shanks (interviews with Mr. Shanks and showing vignettes of his personal life, such as playing hockey)."
        source_dir: "STARGATE_SG1_V1_R1_YR7"
        source_name: "title04.mkv"
      "43":
        title: "Directors Series- 7.03 Fragile Balance with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V1_R1_YR7"
        source_name: "title05.mkv"
      "44":
        title: "SG-1 Beyond the Gate- Christopher Judge (interviews with Mr. Judge and showing his vignettes of his personal life, such as golfing with the producers)"
        source_dir: "STARGATE_SG1_V2_R1_YR7"
        source_name: "title04.mkv"
      "45":
        title: "Directors Series- 7.08 Space Race with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR7"
        source_name: "title05.mkv"
      "46":
        title: "SG-1 Beyond the Gate- Richard Dean Anderson (interviews with Mr. Anderson and showing vignettes of his personal life, such as his trip to Tibet)"
        source_dir: "STARGATE_SG1_V3_R1_YR7"
        source_name: "title04.mkv"
      "47":
        title: "Directors Series- 7.09 Avenger 2.0 with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V3_R1_YR7"
        source_name: "title05.mkv"
      "48":
        title: "Directors Series- 7.16 Death Knell with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V4_R1_YR7"
        source_name: "title05.mkv"
      "49":
        title: "Directors Series with behind the scenes clips of the making of Lost City"
        source_dir: "STARGATE_SG1_V5_R1_YR7"
        source_name: "title04.mkv"
      "50":
        title: "SG-1 Beyond the Gate- Amanda Tapping (interviews with Ms. Tapping and showing vignettes of her personal life, such as hiking with her dog)"
        source_dir: "STARGATE_SG1_V5_R1_YR7"
        source_name: "title05.mkv"
      "51":
        title: "Beyond the Gate- An Air Force Experience with Richard Dean Anderson"
        source_dir: "STARGATE_SG1_V1_R1_YR8"
        source_name: "title04.mkv"
      "52":
        title: "Directors Series- 8.06 Avatar with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR8"
        source_name: "title04.mkv"
      "53":
        title: "Directors Series- 8.08 Covenant with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_SG1_V2_R1_YR8"
        source_name: "title05.mkv"
      "54":
        title: "SuperSoldier- The Making of a Monster"
        source_dir: "STARGATE_SG1_V3_R1_YR8"
        source_name: "title04.mkv"
      "55":
        title: "Beyond the Gate: A Convention Experience with Christopher Judge"
        source_dir: "STARGATE_SG1_V4_R1_YR8"
        source_name: "title04.mkv"
      "56":
        title: "Directors Series- Reckoning with behind the scenes clips of the making of both parts of these episodes"
        source_dir: "SG1_V5_R1_YR8"
        source_name: "title04.mkv"
      "57":
        title: "It Takes a Crew to Raise a Village"
        source_dir: "STARGATE_S9_D1"
        source_name: "title04.mkv"
      "58":
        title: "Directors Series- Avalon with behind the scenes clips of the making of both parts of these episodes"
        source_dir: "STARGATE_S9_D1"
        source_name: "title05.mkv"
      "59":
        title: "Inside the Stargate Props Department Featurette"
        source_dir: "STARGATE_S9_D2"
        source_name: "title04.mkv"
      "60":
        title: "Directors Series- 9.05 The Power That Be with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_S9_D2"
        source_name: "title05.mkv"
      "61":
        title: "Inside the Stargate Special Effects Department Featurette"
        source_dir: "STARGATE_S9_D3"
        source_name: "title04.mkv"
      "62":
        title: "Directors Series 9.09 Prototype with behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_S9_D3"
        source_name: "title05.mkv"
      "63":
        title: "Stargate SG-1- An Introduction to Ben Browder"
        source_dir: "STARGATE_S9_D4"
        source_name: "title04.mkv"
      "64":
        title: "Directors Series- 9.15 Ethon featuring behind the scenes clips of the making of this episode"
        source_dir: "STARGATE_S9_D4"
        source_name: "title05.mkv"
      "65":
        title: "Profile on- Brad Wright"
        source_dir: "STARGATE_S9_D5"
        source_name: "title04.mkv"
      "66":
        title: "Directors Series- 9.19 Crusade with behind the scenes of the making of the episode"
        source_dir: "STARGATE_S9_D5"
        source_name: "title05.mkv"
"""