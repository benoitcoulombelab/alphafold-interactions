#!/bin/bash

# exit when any command fails
set -e

fasta=$1
output=$2
step=${3:-alphafold}
max_template_date=$(date +"%Y-%m-%d")

echo -e "\n\nRun AlphaFold with step ${step} on fasta ${fasta}\n\n"

# load required modules
if [[ -n "$CC_CLUSTER" ]]
then
  module purge
  module load StdEnv/2020
  module load gcc/9.3.0 openmpi/4.0.3 cuda/11.4 cudnn/8.2.0 kalign/2.03 hmmer/3.2.1 openmm-alphafold/7.5.1 \
              hh-suite/3.3.0 python/3.8
  module load alphafold/2.3.2
fi
data_dir="$ALPHAFOLD_SMALL_DATADIR"

### Check values of some environment variables
echo SLURM_JOB_ID="$SLURM_JOB_ID"
echo SLURM_JOB_GPUS="$SLURM_JOB_GPUS"

### Check values of variables
echo "output=${output}"
echo "max_template_date=${max_template_date}"
echo "data_dir=${data_dir}"

if [[ -n "$CC_CLUSTER" ]]
then
  echo "Create AlphaFold virtual environment in ${SLURM_TMPDIR}"
  venv="${SLURM_TMPDIR}/venv"
  virtualenv --no-download "$venv"
  source "${venv}/bin/activate"

  # Install alphafold and its dependencies
  pip install --no-index --upgrade pip
  pip install --no-index --requirement "${ALPHAFOLD}/alphafold-requirements.txt"
  pushd "${venv}/bin"
  git apply "${ALPHAFOLD}/alphafold-${ALPHAFOLD_VERSION}.patch"
  popd
fi

step_parameters=("--use_gpu_relax=True" "--use_precomputed_msas=True")
if [ "${step}" == "prepare" ]
then
  step_parameters=("--prepare" "--use_gpu_relax=False" "--use_precomputed_msas=False")
fi

mkdir -p "${output}"

echo "Start AlphaFold using run_alphafold.py"
run_alphafold.py \
    "${step_parameters[@]}" \
    --fasta_paths="$fasta" \
    --output_dir="${output}" \
    --max_template_date="$max_template_date" \
    --data_dir="$data_dir" \
    --db_preset=reduced_dbs \
    --model_preset=multimer \
    --small_bfd_database_path="${data_dir}/small_bfd/bfd-first_non_consensus_sequences.fasta" \
    --mgnify_database_path="${data_dir}/mgnify/mgy_clusters_2022_05.fa" \
    --template_mmcif_dir="${data_dir}/pdb_mmcif/mmcif_files" \
    --obsolete_pdbs_path="${data_dir}/pdb_mmcif/obsolete.dat" \
    --pdb_seqres_database_path="${data_dir}/pdb_seqres/pdb_seqres.txt" \
    --uniprot_database_path="${data_dir}/uniprot/uniprot.fasta" \
    --uniref90_database_path="${data_dir}/uniref90/uniref90.fasta" \
    --hhblits_binary_path="${EBROOTHHMINSUITE}/bin/hhblits" \
    --hhsearch_binary_path="${EBROOTHHMINSUITE}/bin/hhsearch" \
    --jackhmmer_binary_path="${EBROOTHMMER}/bin/jackhmmer" \
    --kalign_binary_path="${EBROOTKALIGN}/bin/kalign"
