# techno
Taking a number of techno tracks, we:
* normalize them in sample rate and tempo
* order them using a special correlation measurement
* locally align the clips using a sliding window, and finally:
* interpolate to produce a "continuous" mix. N.b. still working to improve accuracy of the tempo normalization. Improved tempo normalization would improve the quality of transitions


(225 lines of python code..tested on Ubuntu)
## result
Five hours of high-energy music for long coding, driving, sports or study sessions:
https://soundcloud.com/ashrichardson/data-science-mix

<img src="soundcloud.png" width="650">

## findings
* Correlation can be used to align techno clips of same tempo for a smooth transition
* Correlation does not take bar lines or counts into account
* Can get wrong answers like being half a beat off!
* More complex method required for reliability

## matrix of correlation between the tracks
<img src="grid.png" width="650">

## clips aligned for correlation on 3.78s window
<img src="correlation.png" width="650">

## files:
* adjust_bpm.py: tempo normalizing
* adjust_rate.py adjust sample rate
* dot.py calculate correlations between tracks
* read.py use between-tracks correlation to establish ordering. Then locally align transitions and interpolate
* cat.py put the track segments and transitions together into one file
