import os.path
import sys
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, ANY, patch

import pytest
from Bio.PDB import PDBParser, NeighborSearch

from afpairs import InteractionScore


@pytest.fixture
def mock_testclass():
    _interaction_score = InteractionScore.interaction_score
    _potential_interactor_atoms = InteractionScore.potential_interactor_atoms
    _search_interactions = InteractionScore.search_interactions
    _get_chain = InteractionScore.get_chain
    _write_residues = InteractionScore.write_residues
    _write_atoms = InteractionScore.write_atoms
    yield
    InteractionScore.interaction_score = _interaction_score
    InteractionScore.potential_interactor_atoms = _potential_interactor_atoms
    InteractionScore.search_interactions = _search_interactions
    InteractionScore.get_chain = _get_chain
    InteractionScore.write_residues = _write_residues
    InteractionScore.write_atoms = _write_atoms


def test_main(testdir, mock_testclass, capsys):
    InteractionScore.interaction_score = MagicMock(return_value="2.3")
    stdin_file = "stdin.txt"
    open(stdin_file, 'w').close()
    with open(stdin_file, 'r') as stdin_in, patch('sys.stdin', stdin_in):
        InteractionScore.main()
    InteractionScore.interaction_score.assert_called_once_with(
        pdb=ANY, radius=6.0, weight=False, first_chains=["A"], second_chains=["B"],
        residues=None, atoms=None)
    pdb = InteractionScore.interaction_score.call_args.kwargs['pdb']
    assert isinstance(pdb, TextIOWrapper)
    assert pdb.mode == "r"
    out, err = capsys.readouterr()
    sys.stdout.write(out)
    assert out == "2.3\n"


def test_main_parameters(testdir, mock_testclass):
    input_file = "input.pdb"
    open(input_file, 'w').close()
    residue_pairs_file = "residues.txt"
    atom_pairs_file = "atoms.txt"
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(return_value="2.3")
    InteractionScore.main(["-a", "A,B", "-b", "C,D", "-r", "8", "-w",
                           "-R", residue_pairs_file, "-A", atom_pairs_file, "-o", output_file, input_file])
    InteractionScore.interaction_score.assert_called_once_with(
        pdb=ANY, radius=8, weight=True, first_chains=["A", "B"], second_chains=["C", "D"],
        residues=ANY, atoms=ANY)
    assert InteractionScore.interaction_score.call_args.kwargs["pdb"].name == input_file
    assert InteractionScore.interaction_score.call_args.kwargs["pdb"].mode == "r"
    assert InteractionScore.interaction_score.call_args.kwargs["residues"].name == residue_pairs_file
    assert InteractionScore.interaction_score.call_args.kwargs["residues"].mode == "w"
    assert InteractionScore.interaction_score.call_args.kwargs["atoms"].name == atom_pairs_file
    assert InteractionScore.interaction_score.call_args.kwargs["atoms"].mode == "w"
    os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "2.3\n"


def test_main_long_parameters(testdir, mock_testclass):
    input_file = "input.pdb"
    open(input_file, 'w').close()
    residue_pairs_file = "residues.txt"
    atom_pairs_file = "atoms.txt"
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(return_value="2.3")
    InteractionScore.main(["--first", "A,B", "--second", "C,D", "--radius", "8", "--weight",
                           "--residues", residue_pairs_file, "--atoms", atom_pairs_file, "--output", output_file,
                           input_file])
    InteractionScore.interaction_score.assert_called_once_with(
        pdb=ANY, radius=8, weight=True, first_chains=["A", "B"], second_chains=["C", "D"],
        residues=ANY, atoms=ANY)
    assert InteractionScore.interaction_score.call_args.kwargs["pdb"].name == input_file
    assert InteractionScore.interaction_score.call_args.kwargs["pdb"].mode == "r"
    assert InteractionScore.interaction_score.call_args.kwargs["residues"].name == residue_pairs_file
    assert InteractionScore.interaction_score.call_args.kwargs["residues"].mode == "w"
    assert InteractionScore.interaction_score.call_args.kwargs["atoms"].name == atom_pairs_file
    assert InteractionScore.interaction_score.call_args.kwargs["atoms"].mode == "w"
    os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "2.3\n"


def test_interaction_score(testdir, mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    score = InteractionScore.interaction_score(pdb=pdb)
    assert score == 580
    score = InteractionScore.interaction_score(pdb=pdb, weight=True)
    assert abs(score - 31.48) < 0.01


def test_interaction_score_write_residues(testdir, mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    residue_pairs_file = "residues.txt"
    InteractionScore.write_residues = MagicMock()
    with open(residue_pairs_file, 'w') as residue_pairs_out:
        InteractionScore.interaction_score(pdb=pdb, residues=residue_pairs_out)
        InteractionScore.write_residues.assert_called_once_with(ANY, residue_pairs_out)
    residue_pairs = InteractionScore.write_residues.call_args.args[0]
    chain_a = residue_pairs[0][0].get_parent()
    chain_b = residue_pairs[0][1].get_parent()
    assert (chain_a[13], chain_b[1147]) in residue_pairs
    assert (chain_a[13], chain_b[1148]) in residue_pairs
    assert (chain_a[14], chain_b[1147]) in residue_pairs
    assert (chain_a[14], chain_b[1148]) in residue_pairs
    assert (chain_a[15], chain_b[1148]) in residue_pairs
    assert (chain_a[15], chain_b[1149]) in residue_pairs


def test_interaction_score_write_atoms(testdir, mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    atom_pairs_file = "atoms.txt"
    InteractionScore.write_atoms = MagicMock()
    with open(atom_pairs_file, 'w') as atom_pairs_out:
        InteractionScore.interaction_score(pdb=pdb, atoms=atom_pairs_out)
        InteractionScore.write_atoms.assert_called_once_with(ANY, atom_pairs_out)
    atoms_pairs = InteractionScore.write_atoms.call_args.args[0]
    chain_a = atoms_pairs[0][0].get_parent().get_parent()
    chain_b = atoms_pairs[0][1].get_parent().get_parent()
    assert (chain_a[13]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CD1"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[13]["SG"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[14]["CG"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CG"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CD1"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD2"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1149]["CB"]) in atoms_pairs


def test_potential_interactor_atoms(mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    chain_a = structure[0]["A"]
    atoms = InteractionScore.potential_interactor_atoms(chain_a)
    assert len(atoms) == 7383
    assert atoms[0] == chain_a[1]["CB"]
    assert atoms[1] == chain_a[1]["CG"]
    assert atoms[2] == chain_a[1]["SD"]
    assert atoms[3] == chain_a[1]["CE"]
    assert atoms[4] == chain_a[2]["CB"]
    assert atoms[5] == chain_a[2]["CG"]
    assert atoms[6] == chain_a[2]["CD2"]
    assert atoms[7] == chain_a[2]["ND1"]
    assert atoms[8] == chain_a[2]["CE1"]
    assert atoms[9] == chain_a[2]["NE2"]
    assert atoms[10] == chain_a[6]["CB"]
    assert atoms[11] == chain_a[6]["CG"]
    assert atoms[12] == chain_a[6]["CD"]
    chain_b = structure[0]["B"]
    atoms = InteractionScore.potential_interactor_atoms(chain_b)
    assert len(atoms) == 4696
    assert atoms[0] == chain_b[1]["CB"]
    assert atoms[1] == chain_b[1]["CG"]
    assert atoms[2] == chain_b[1]["SD"]
    assert atoms[3] == chain_b[1]["CE"]
    assert atoms[4] == chain_b[2]["CB"]
    assert atoms[5] == chain_b[2]["CG"]
    assert atoms[6] == chain_b[2]["CD1"]
    assert atoms[7] == chain_b[2]["CD2"]
    assert atoms[8] == chain_b[2]["CE1"]
    assert atoms[9] == chain_b[2]["CE2"]
    assert atoms[10] == chain_b[2]["OH"]
    assert atoms[11] == chain_b[2]["CZ"]
    assert atoms[12] == chain_b[3]["CB"]
    assert atoms[13] == chain_b[3]["CG"]
    assert atoms[14] == chain_b[3]["OD1"]
    assert atoms[15] == chain_b[3]["OD2"]


def test_search_interactions_residue(mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    chain_a = structure[0]["A"]
    atoms_a = [chain_a[13]["CB"], chain_a[13]["SG"],
               chain_a[14]["CB"], chain_a[14]["CG"], chain_a[14]["CD"],
               chain_a[15]["CB"], chain_a[15]["CG"], chain_a[15]["CD1"], chain_a[15]["CD2"]]
    chain_b = structure[0]["B"]
    atoms_b = [chain_b[1147]["CB"], chain_b[1147]["OG"],
               chain_b[1148]["CB"], chain_b[1148]["CG"], chain_b[1148]["CD1"], chain_b[1148]["CD2"],
               chain_b[1149]["CB"], chain_b[1149]["CG1"], chain_b[1149]["CG2"]]
    neighbor_search = NeighborSearch(atoms_a + atoms_b)
    residue_pairs = InteractionScore.search_interactions(neighbor_search=neighbor_search, radius=6.0, level='R')
    assert len(residue_pairs) == 6
    assert (chain_a[13], chain_b[1147]) in residue_pairs
    assert (chain_a[13], chain_b[1148]) in residue_pairs
    assert (chain_a[14], chain_b[1147]) in residue_pairs
    assert (chain_a[14], chain_b[1148]) in residue_pairs
    assert (chain_a[15], chain_b[1148]) in residue_pairs
    assert (chain_a[15], chain_b[1149]) in residue_pairs


def test_search_interactions_atom(mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    chain_a = structure[0]["A"]
    atoms_a = [chain_a[13]["CB"], chain_a[13]["SG"],
               chain_a[14]["CB"], chain_a[14]["CG"], chain_a[14]["CD"],
               chain_a[15]["CB"], chain_a[15]["CG"], chain_a[15]["CD1"], chain_a[15]["CD2"]]
    chain_b = structure[0]["B"]
    atoms_b = [chain_b[1147]["CB"], chain_b[1147]["OG"],
               chain_b[1148]["CB"], chain_b[1148]["CG"], chain_b[1148]["CD1"], chain_b[1148]["CD2"],
               chain_b[1149]["CB"], chain_b[1149]["CG1"], chain_b[1149]["CG2"]]
    neighbor_search = NeighborSearch(atoms_a + atoms_b)
    atoms_pairs = InteractionScore.search_interactions(neighbor_search=neighbor_search, radius=6.0, level='A')
    assert len(atoms_pairs) == 25
    assert (chain_a[13]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CD1"]) in atoms_pairs
    assert (chain_a[13]["CB"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[13]["SG"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CB"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[14]["CD"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[14]["CG"], chain_b[1147]["CB"]) in atoms_pairs
    assert (chain_a[14]["CG"], chain_b[1147]["OG"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CB"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CD1"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD2"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CB"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CD2"]) in atoms_pairs
    assert (chain_a[15]["CG"], chain_b[1148]["CG"]) in atoms_pairs
    assert (chain_a[15]["CD1"], chain_b[1149]["CB"]) in atoms_pairs


def test_get_chain(mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    chain_a = structure[0]["A"]
    chain_b = structure[0]["B"]
    chain = InteractionScore.get_chain(chain_a[1], 'R')
    assert chain == chain_a
    chain = InteractionScore.get_chain(chain_b[2], 'R')
    assert chain == chain_b
    chain = InteractionScore.get_chain(chain_a[1]["C"], 'A')
    assert chain == chain_a
    chain = InteractionScore.get_chain(chain_b[2]["C"], 'A')
    assert chain == chain_b
    try:
        InteractionScore.get_chain(chain_b, 'C')
    except AssertionError:
        assert True
    else:
        assert False, "Expected an AssertionError"


def test_write_residues(testdir, mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    residue_pairs = [(structure[0]["A"][1], structure[0]["B"][1]),
                     (structure[0]["A"][2], structure[0]["B"][2])]
    output_file = "residues.txt"
    with open(output_file, 'w') as output_out:
        InteractionScore.write_residues(residue_pairs=residue_pairs, output_file=output_out)
    os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "Chain A\tResidue number A\tResidue name A\t" \
                                       "Chain B\tResidue number B\tResidue name B\n"
        assert output_in.readline() == "A\t1\tMET\tB\t1\tMET\n"
        assert output_in.readline() == "A\t2\tHIS\tB\t2\tTYR\n"


def test_write_atoms(testdir, mock_testclass):
    pdb = Path(__file__).parent.joinpath("POLR2A_POLR2B_ranked_0.pdb")
    parser = PDBParser()
    structure = parser.get_structure("unknown", pdb)
    atom_pairs = [(structure[0]["A"][1]["C"], structure[0]["B"][1]["N"]),
                  (structure[0]["A"][2]["CA"], structure[0]["B"][2]["O"])]
    output_file = "atoms.txt"
    with open(output_file, 'w') as output_out:
        InteractionScore.write_atoms(atom_pairs=atom_pairs, output_file=output_out)
    os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "Chain A\tResidue number A\tResidue name A\tAtom A\t" \
                                       "Chain B\tResidue number B\tResidue name B\tAtom B\n"
        assert output_in.readline() == "A\t1\tMET\tC\tB\t1\tMET\tN\n"
        assert output_in.readline() == "A\t2\tHIS\tCA\tB\t2\tTYR\tO\n"
