import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import random


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


# settings
out_pdf = './test.pdf'

# some random data
data = []
for i in range(0, 5000):
    data.append([i, float(i + random.randrange(-50, 50))/100, 5])

pdf = matplotlib.backends.backend_pdf.PdfPages(out_pdf)
cnt = 0
figs = plt.figure()
for data_chunk in chunks(data, 600):
    plot_num = 311
    fig = plt.figure(figsize=(10, 10))  # inches
    for sub_chunk in chunks(data_chunk, 200):
        cnt += 1
        d = [a[0] for a in sub_chunk]
        z = [a[1] for a in sub_chunk]
        zv = [a[2] for a in sub_chunk]

        print(plot_num)
        plt.subplot(plot_num)
        # plot profile, define styles
        plt.plot(d, z, 'r', linewidth=0.75)
        plt.plot(d, z, 'ro', alpha=0.3, markersize=3)
        plt.plot(d, zv, 'k--', linewidth=0.5)
        plt.xlabel('Distance from start')
        plt.ylabel('Elevation')
        plt.title('Profile {0} using Python matplotlib'.format(cnt))

        # change font size
        # plt.rcParams.update({'font.size': 8})
        plot_num += 1
    plt.tight_layout()
    pdf.savefig(fig)

pdf.close()
