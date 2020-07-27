# Genomics Live Demo

## Set-up

Beforehand we need to run:

```bash
# gem-mapper on path
PATH=$PATH:${HOME}/faasm-experiments-bm/third-party/gem3-mapper/bin

# Simple terminal
export PS1="$ "
```

You also need to:
 
- Make your terminal font massive
- Switch to a black on white theme
- Go full screen on your terminal with no tabs

Run the following:

```
cd ~/faasm-bm
source workon.sh
cd ../faasm-experiments-bm
inv toolchain.version
```

## Start Recording

To record the terminal, you need to:

```
script --timing=time.txt script.log
```

To stop recording press `ctrl + D`.

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

inv genomics.mapping-native --nthreads=10
inv genomics.mapping-native --nthreads=20
```

List the output:

```bash
du -sh ~/faasm/data/genomics/output 
```

## Faasm Demo

Upload a file, then start running the whole script

```bash
inv state.shared-file ~/faasm/data/genomics/reads_1.fq reads_1.fq
```

Now run the whole thing:

```bash
inv genomics.mapping
```

Download the output:

```bash
inv state.download gene map_out_1_10 /tmp/faasm_out_1_10.sam

inv genomics.download-output
```
