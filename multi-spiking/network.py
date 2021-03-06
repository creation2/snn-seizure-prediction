import copy
import numpy as np
INITIAL_WEIGHT = 1
NEURON_THRESHOLD = 1

# Weights contains an entry for every synapse, organized by four
# parameters:
# * w - the layer of the network of the destination neuron
# * x - the neuron index of the destination neuron within its layer
# * y - the neuron index of the source neuron within its layer
# * z - the index among the multiple synapses connecting those two
#
# Note that a (w, x) pair is sufficient to uniquely identify a neuron.
# Also, contrary to the paper, layers are numbered going forwards, and are
# zero-based. The input layer is 0, and the output layer (in this case) is 2.


def initWeights(layerNeuronCounts, synapsesPerConnection):
    weights = []

    # sourceLayerNumber uses zero-based indexing
    # It stops one short of the end because output neurons have no
    # further connections
    for destinationLayerNumber in range(1, len(layerNeuronCounts)):
        xs = range(layerNeuronCounts[destinationLayerNumber])
        ys = range(layerNeuronCounts[destinationLayerNumber - 1])
        # Since synapses/connection is constant throughout the network,
        # we can reuse this across the network. However, we need to make
        # copies so that different weights don't influence each other.
        eachConnection = [INITIAL_WEIGHT] * synapsesPerConnection
        # Create the connections for each destination neuron, and then each
        # source neuron. Since we're building these from the bottom up,
        # they appear to go backwards.
        layerConnections = [
            [copy.deepcopy(eachConnection) for y in ys]
            for x in xs
        ]
        weights.append(layerConnections)
    return weights


# This produces an array that functions as a map from a synapse index (z) to
# its respective delay.
def synapseDelays(synapseCount, lastOutput):
    synapseDelay = [1]
    # The int works just like mathematically - it rounds down. I think I could
    # use the double slash here, but this is more clear.
    increment = int(lastOutput / synapseCount)
    for i in range(0, synapseCount - 1):
        synapseDelay.append(synapseDelay[i] + increment)
    return synapseDelay


def spikeResponse(time, timeDecay):
    if time > 0:
        return (time/timeDecay) * math.exp(1 - (time/timeDecay))
    else:
        return 0


def refractoriness(time, refractorinessDecay):
    if time > 0:
        return -2 * NEURON_THRESHOLD * math.exp(-time / refractorinessDecay)
    else:
        return 0


def networkError(observed, expected):
    o = np.array(observed)
    e = np.array(expected)
    return 1/2 * sum((o - e) ** 2)


# The equation this models (in case this ever goes to a Jupyter notebook):
# $$ x_j(t) = \sum_{i=1}^{N_{l+1}} \sum_{k=1}^{K} \sum_{g=1}^{G_i} w^k_{ij}
# \varepsilon(t-t_i^{(g)}-d^k) + \rho(t-t_j^{(f)}) $$

# Arguments:
# weights: same format as the output of initWeights
# presynapticLayerStates: indices are [neuron index][spike index]
# currentState: an ordered array of spike times for the current neuron
# time: the whole-simulation time
# w and x - as defined in top comment
def newNeuronState(weights, presynapticLayerStates, currentState, time, w, x):
    internalState = 0
    # y (with meaning as above) is "i" in the paper
    for y in range(len(presynapticStates)):
        # synapse number should be constant throughout the network, but for
        # clarity's sake is computed in this loop. It is "k" in the paper.
        for z in range(len(presynapticStates[y])):
            # "g" in the paper
            for spikeTime in presynapticStates[y]:
                weight = weights[w][x][y][z]
                adjustedTime = time - (spikeTime + synapseDelay[z])
                internalState += weight * spikeResponse(adjustedTime)
    timeSinceLastSpike = time - currentState[-1]
    internalState += refractoriness(timeSinceLastSpike)
    return internalState


class MultiSpikingNetwork(object):
    """
    """
    def __init__(self, layerNeuronCounts, synapsesPerConnection,
                 encodingInterval, refractorinessDecay):
        super(MultiSpikingNetwork, self).__init__()
        self.layerNeuronCounts = layerNeuronCounts
        self.weights = initWeights(layerNeuronCounts, synapsesPerConnection)
        self.encodingInterval = encodingInterval
        self.refractorinessDecay = refractorinessDecay  # $\tau_r$ in the paper
        self.timeDecay = encodingInterval + 1  # plain $\tau$ in the paper

    def makeXorNetwork():
        # Explanation of inputs:
        # 3: 2 inputs + 1 bias neuron
        # 5: Arbitary, from what I can tell
        # 1: one output (of the XOR function)

        # 4: smallest number needed to model the problem
        # 6: Conformity with Bohte et al. (2002)
        # 80: Chosen by trial-and-error
        return MultiSpikingNetwork([3, 5, 1], 4, 6, 80)

    def simulate(self, duration, lastOutput, inputs):
        # Do some basic sanity checks on the input
        # Make sure that there are the right number of inputs
        assert len(inputs) == len(self.weights[0])
        # Make sure that there are no delays that could possibly overrun the
        # end of the simulation (rendering them useless)
        assert lastOutput <= duration

        for time in range(duration):
            # for every layer in the network except the first, which is not a
            # destination for any signals...
            for w in range(1, len(self.weights)):
                # for every neuron in that layer...
                for x in range(0, len(self.weights[w])):
                    # This part of the loop is specific to each individual
                    # neuron. For every neuron presynaptic to the (w, x)
                    # neuron...
                    for y in range(0, len(self.weights[w - 1])):
                        for z in range(self.synapsesPerConnection):
                            for spikeTime in inputs[y]:
                                newState = newNeuronState(self.weights, inputs
                                                          [], time, w, x)


# run this code only if executed, not when imported
if __name__ == "__main__":
    print(MultiSpikingNetwork.makeXorNetwork().weights)
