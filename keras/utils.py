import numpy

def create_data_subset(inputset, outputset, subset=0, seed=False):
    '''
    This function gives subsets of input and output data in no guaranteed order and their size.
    subset - Share of data expressed as a percentage.
    '''
    if seed:
        numpy.random.seed(seed)

    if subset > 0 and subset < 100:
        n_samples = int(len(inputset)/100 * subset)
        print(n_samples, ' samples in the new set.', len(inputset))
        chosen = numpy.random.choice(len(inputset), n_samples, replace=False)
        inputset = inputset[chosen]
        outputset = outputset[chosen]
    
    return inputset, outputset, len(inputset)


def generate_graphs(estimator, modelname):
    
    base = 'graphs/categorical_crossentropy/' + modelname
    estimator.draw_metric(metric='loss', filepath= base)
    estimator.draw_metric(metric='loss', ylim=(2.15, 2.5), filepath= base + '_ylim(2.15,2.5)')
    estimator.draw_metric_across_folds(metric='loss', filepath= base + '_10fold')
    estimator.draw_metric_across_folds(metric='loss', ylim=(2.15, 2.5), filepath= base + '_10fold_ylim(2.15,2.5)')
    
    base = 'graphs/mean_absolute_error/' + modelname
    estimator.draw_metric(metric='mean_absolute_error', filepath= base)
    estimator.draw_metric(metric='mean_absolute_error', ylim=(0.02, 0.05), filepath= base + '_ylim(0.02,0.05)') 
    estimator.draw_metric_across_folds(metric='mean_absolute_error', filepath= base + '_10fold')
    estimator.draw_metric_across_folds(metric='mean_absolute_error', ylim=(0.02, 0.05), filepath= base + '_10fold_ylim(0.02,0.05)')
    
    base = 'graphs/root_mean_squared_error/' + modelname
    estimator.draw_metric(metric='root_mean_squared_error', filepath= base)
    estimator.draw_metric(metric='root_mean_squared_error', ylim=(0.025, 0.05), filepath= base + '_ylim(0.025,0.05)')
    estimator.draw_metric_across_folds(metric='root_mean_squared_error', filepath= base + '_10fold')
    estimator.draw_metric_across_folds(metric='root_mean_squared_error', ylim=(0.025, 0.05), filepath= base + '_10fold_ylim(0.025,0.05)')







