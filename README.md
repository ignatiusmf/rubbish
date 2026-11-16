# rubbish

A tiny command-line program that talks rubbish: it prints procedurally generated nonsense sentences.

## Usage

```
./rubbish.py                 # one sentence
./rubbish.py -n 5            # five sentences (--count 5)
./rubbish.py -s 42           # reproducible output (--seed 42)
./rubbish.py --seed 42 --count 5
```

## Example

```
$ ./rubbish.py --seed 7 -n 3
The dusty umbrella slowly polishes an orange pancake.
The oblong trombone patiently polishes a rusty lantern.
The enormous stapler slowly photographs an orange kettle.
```

Every sentence has the form `The <adjective> <noun> <adverb> <verb> <a|an> <adjective> <noun>.`

## Tests

```
python3 -m unittest -v
```

Python 3, standard library only (tested with 3.14).
