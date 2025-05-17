### CitationChecker

Using the semantic scholar API, this script checks if the bibliography is up-to-date. 
If the paper can only be found in ArXiv, the bib will not be updated; otherwise, it will update the bib with the corresponding information. 

 ```bash
 python bibChecker.py -i input_path/bib.bib -o output_path/update_bib.bib -c output_path/updates.csv 
```

Other optional arguments: 
```bash
--delay -d "Delay between API calls in seconds (default: 1.0)"
```
