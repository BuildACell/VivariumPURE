import os

from vivarium.core.composer import Composer
from vivarium.core.composition import (
    COMPOSITE_OUT_DIR,
    simulate_composer,
)
from vivarium.plots.simulation_output import plot_simulation_output
from vivarium.library.units import units

# processes
from vivarium.processes.tree_mass import TreeMass

from pure.plots.gene_expression import plot_gene_expression_output
from pure.processes.legacy.transcription import Transcription, UNBOUND_RNAP_KEY
from pure.processes.legacy.translation import Translation, UNBOUND_RIBOSOME_KEY
from pure.processes.legacy.degradation import RnaDegradation, DEFAULT_TRANSCRIPT_DEGRADATION_KM
from pure.data.amino_acids import amino_acids
from pure.data.nucleotides import nucleotides
from pure.data.plasmids.gfp import gfp_plasmid_config


NAME = 'gene_expression'

class GeneExpression(Composer):

    defaults = {
        'global_path': ('global',),
        'initial_mass': 1339.0 * units.fg,
        'time_step': 1.0,
        'transcription': {},
        'translation': {},
        'degradation': {},
    }

    def __init__(self, config):
        super().__init__(config)

    def generate_processes(self, config):
        transcription_config = config['transcription']
        translation_config = config['translation']
        degradation_config = config['degradation']

        # update timestep
        transcription_config.update({'time_step': config['time_step']})
        translation_config.update({'time_step': config['time_step']})
        degradation_config.update({'time_step': config['time_step']})

        # make the processes
        transcription = Transcription(transcription_config)
        translation = Translation(translation_config)
        degradation = RnaDegradation(degradation_config)
        mass_deriver = TreeMass(config.get('mass_deriver', {
            'initial_mass': config['initial_mass']}))

        return {
            'mass_deriver': mass_deriver,
            'transcription': transcription,
            'translation': translation,
            'degradation': degradation,
        }

    def generate_topology(self, config):
        global_path = config['global_path']

        return {
            'mass_deriver': {
                'global': global_path},

            'transcription': {
                'chromosome': ('chromosome',),
                'molecules': ('molecules',),
                'proteins': ('proteins',),
                'transcripts': ('transcripts',),
                'factors': ('concentrations',),
                'global': global_path},

            'translation': {
                'ribosomes': ('ribosomes',),
                'molecules': ('molecules',),
                'transcripts': ('transcripts',),
                'proteins': ('proteins',),
                'concentrations': ('concentrations',),
                'global': global_path},

            'degradation': {
                'transcripts': ('transcripts',),
                'proteins': ('proteins',),
                'molecules': ('molecules',),
                'global': global_path}
        }


# test
def run_gene_expression(total_time=10, out_dir='out'):
    timeseries = test_gene_expression(total_time)
    plot_settings = {
        'name': 'gene_expression',
        'ports': {
            'transcripts': 'transcripts',
            'molecules': 'molecules',
            'proteins': 'proteins'}}
    plot_gene_expression_output(timeseries, plot_settings, out_dir)

    sim_plot_settings = {'max_rows': 25}
    plot_simulation_output(timeseries, sim_plot_settings, out_dir)


def test_gene_expression(total_time=10):
    # load the composer
    composer_config = {
        'external_path': ('external',),
        'global_path': ('global',),
        'agents_path': ('..', '..', 'cells',),
        'transcription': {
            'sequence': gfp_plasmid_config['sequence'],
            'templates': gfp_plasmid_config['promoters'],
            'genes': gfp_plasmid_config['genes'],
            'promoter_affinities': gfp_plasmid_config['promoter_affinities'],
            'transcription_factors': ['tfA', 'tfB'],
            'elongation_rate': 10.0
        },
        'translation': {
            'sequences': gfp_plasmid_config['sequence'],
            'templates': gfp_plasmid_config['promoters'],
            'transcript_affinities': {},
            'elongation_rate': 5.0,
        },
        'degradation': {
            'sequences': gfp_plasmid_config['sequence'],
            'catalytic_rates': {
                'endoRNAse': 0.1
            },
            'michaelis_constants': {
                'transcripts': {
                    'endoRNAse': {
                        'GFP_RNA': DEFAULT_TRANSCRIPT_DEGRADATION_KM,
                    }
                }
            }
        }
    }
    composer = GeneExpression(composer_config)

    molecules = {
        nt: 1000
        for nt in nucleotides.values()}
    molecules.update({
        aa: 1000
        for aa in amino_acids.values()})

    proteins = {
        polymerase: 100
        for polymerase in [
                UNBOUND_RNAP_KEY,
                UNBOUND_RIBOSOME_KEY]}

    # proteins.update({
    #     factor: 1
    #     for factor in [
    #             'tfA',
    #             'tfB']})

    # simulate
    settings = {
        'timestep': 1,
        'total_time': total_time,
        'initial_state': {
            'proteins': proteins,
            'molecules': molecules}}
    return simulate_composer(composer, settings)


# python pure/composites/legacy/gene_expression.py
if __name__ == '__main__':
    out_dir = os.path.join(COMPOSITE_OUT_DIR, NAME)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    run_gene_expression(600, out_dir)
