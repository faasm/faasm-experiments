# Genomics Live Demo

## Set-up

Beforehand we need to run:

```bash
# gem-mapper on path
PATH=$PATH:${HOME}/fasm-experiments-bm/third-party/gem3-mapper/bin

# Simple terminal
export PS1="$ "
```

You also need to:
 
- Make your terminal font massive
- Switch to a black on white theme
- Go full screen on your terminal with no tabs

## Native Demo

Show data on local machine:

```bash
cd ~/faasm/data/genomics
ls 

du -sh .
du -sh reads*
du -sh index* | less
```

Show running a read vs. an index:

```bash
gem-mapper -i reads_1.fq -I index_10.gem -o /tmp/read1_index10.sam
```

Show running the whole script

```bash
cd ~/faasm-experiments-bm 

fm genomics.mapping-native
```

List the output:

```bash
ls ~/faasm/data/genomics/output/native
du -sh ~/faasm/data/genomics/output 
```

## Faasm Demo

Upload a file, then start running the whole script

```bash
fm state.shared-file ~/faasm/data/genomics/reads_1.fq reads_1.fq

fm genomics.upload-data
```

Now run the whole thing:

```bash
fm genomics.mapping
```

Download the output:

```bash
fm state.download gene map_out_1_10 /tmp/faasm_out_1_10.sam

fm genomics.download-output
```
