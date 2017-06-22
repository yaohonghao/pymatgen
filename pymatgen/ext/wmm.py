"""
This module creates an interface to the JHU kpoints servlet
"""

__author__ = "Joseph Montoya"
__copyright__ = "Copyright 2017, The Materials Project"
__maintainer__ = "Joseph Montoya"
__email__ = "montoyjh@lbl.gov"
__date__ = "June 22, 2017"


def get_from_wmm(structure, min_distance=0, min_total_kpoints=1, 
                 kppra=None, gap_distance=7, remove_symmetry=None, 
                 include_gamma="auto", header="simple", incar=None):
    """
    Get kpoints object from JHU servlet, per Wisesa-McGill-Mueller
    methodology.  Refer to http://muellergroup.jhu.edu/K-Points.html
    and P. Wisesa, K. A. McGill, T. Mueller, Phys. Rev. B 93, 
    155109 (2016)

    Args:
        structure (Structure): structure object
        min_distance (float): The minimum allowed distance 
            between lattice points on the real-space superlattice 
        min_total_kpoints (int): The minimum allowed number of 
            total k-points in the Brillouin zone.
        kppra (float): minimum k-points per reciprocal atom.
        gap_distance (float): auto-detection threshold for
            non-periodicity (in slabs, nanowires, etc.)
        remove_symmetry (string): optional flag to control
            symmetry options, can be none, structural, 
            time_reversal, or all
        include_gamma (string or bool): whether to include
            gamma point
        header (string): "verbose" or "simple", denotes
            the verbosity of the header
        incar (Incar): incar object to upload
    """
    config = locals()
    config.pop("structure", "incar")

    # Generate PRECALC string
    precalc = ''.join(["{}={}\n".format(k, v) for k, v in config.items()])
    precalc = precalc.replace('_', '').upper()
    precalc = precalc.replace('REMOVESYMMETRY', 'REMOVE_SYMMETRY')
    precalc = precalc.replace('TIMEREVERSAL', 'TIME_REVERSAL')

    url = "http://muellergroup.jhu.edu:8080/PreCalcServer/PreCalcServlet"

    with ScratchDir(".") as temp_dir:
        with open("PRECALC", 'w') as f:
            f.write(precalc)
        structure.to(filename="POSCAR")
        files = [("fileupload", open("PRECALC")),
                 ("fileupload", open("POSCAR"))]
        if incar:
            incar.write_file("INCAR")
            files.append(("fileupload", open("INCAR")))
        r = requests.post(url, files=files)

    return Kpoints.from_string(r.text)


