targets='DoAr_16 DoAr_33 YLW_8 GSS_39 DoAr_24E AS_206 GSS_26 WSB_31 VSSG_1 DoAr_25 IRS_37 IRS_41 IRS_51 IRS_39 YLW_47 WSB_60 HBC_266 DoAr_44'
tracks='track3b'
rxs='rx230 rx240'
sidebands='lsb usb'

refant='6'

# creating a directory to host self-calibrated data
#rm -rf selcal_Miriad
#mkdir selcal_Miriad

#rm -rf *.model
#rm -rf *.txt
#rm -rf *.sel
#rm -rf *.gain
#rm -rf *rx*
#cp ~/data_reduction/SMAOphiuchusDisk_track1_reduction/imaging_box/center_track2_2.txt .

# looping over observations on varios target sources
for track in $tracks
do
  for rx in $rxs
  do

    # set reference antenna and solution interval
    if [ $track = 'track1' ]
    then
      interval='5'
      refant='6'
      cellsize=0.06
      imsize=512
    fi

    if [ $track = 'track2a' ]
    then
      interval='5'
      refant='6'
      cellsize=0.125
      imsize=512
    fi    

    if [ $track = 'track3b' ]
    then
      interval='5'
      refant='6'
      cellsize=0.125
      imsize=512
    fi
    
    for sideband in $sidebands
    do

      for target in $targets
      do
        datadir='../../calibrated_Miriad/'$track'/cal/'
        imdir='../../calibrated_Miriad/'$track'/ch0/'

        vishead=$target'.'$rx'.'$sideband'.'$track

	# copy over visibility data
        vis=$vishead'.cal.miriad'
        cp -r $datadir$vis ./
	uvflag vis=$vis edge=64,64,0 flagval="f"

	if [ $rx = 'rx345' ] && [ $sideband = 'lsb' ]
	then
		# copy over image model
		model=$target'.rx345.lsb.'$track'.10.ch0.model'
		cp -r $imdir$model ./

	else
		model=$vishead'.10.ch0.model'
                cp -r $imdir$model ./

	fi

        # copy over image model
#        model=$target'.rx345.usb.model'
#        cp -r ../v2022Aug03/$model ./

        # convert to Stokes I data
        rm -rf $vis'.i'
        uvaver vis=$vis options=nopass,nocal,nopol out=$vis'.i' stokes=ii
 
        # produce ascii output for the self-calibration solution
        gaintable=$target'_'$track'.'$rx'.'$sideband'.1p.gain'
        rm -rf $gaintable
        int='0.1'
        selfcal vis=$vis'.i' model=$model \
                out=$gaintable \
                options='pha,mfs' \
                interval=$interval refant=$refant


        # perform gain self-claibration solution
        selfcal vis=$vis'.i' model=$model \
                options='pha,mfs' \
                interval=$interval refant=$refant
 

        # inspecting the solution and yield ascii output for solution table
        rm -rf $gaintable'.txt'
        gpplt vis=$gaintable yaxis=phase nxy=1,1 log=$gaintable'.txt' # device=/xw

        # apply calibration solution
        rm -rf $vis'.sel'
        uvaver vis=$vis'.i' options=nopass,nopol out=$vis'.sel'
	

        rm -rf $vis
        cp -r $datadir$vis ./
        uvflag vis=$vis edge=64,64,0 flagval="f"


        rm -rf $vishead'.ch0.miriad'
        uvlin vis=$vishead'.cal.miriad' \
              out=$vishead'.ch0.miriad' \
              chans='64,960' \
              mode=continuum options=nocal,nopass,nopol order=1

        rm -rf $vishead'.line.miriad'
        uvlin vis=$vishead'.cal.miriad' \
              out=$vishead'.line.miriad' \
              chans='64,960' \
              mode=line options=nocal,nopass,nopol order=1


        # creating non-self-calibrated image
        rm -rf $vishead'.ch0.dirty'
        rm -rf $vishead'.ch0.beam'
        invert vis=$vishead'.cal.miriad' \
               options=systemp,mfs,double robust=2.0 \
               map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' cell=$cellsize imsize=$imsize
#               select='uvrange(0,80)'

        rm -rf $vishead'.ch0.dirty.fits'
        rm -rf $vishead'.ch0.beam.fits'
        fits in=$vishead'.ch0.dirty' op=xyout out=$vishead'.ch0.dirty.fits'
        fits in=$vishead'.ch0.beam' op=xyout out=$vishead'.ch0.beam.fits'

        rm -rf $vishead'.10.ch0.model'
        rm -rf $vishead'.10.ch0.model.fits'
        clean map=$vishead'.ch0.dirty' \
                beam=$vishead'.ch0.beam' \
                out=$vishead'.10.ch0.model' cutoff=0.01 niters=10 options=positive
        fits in=$vishead'.10.ch0.model' op=xyout out=$vishead'.10.ch0.model.fits'

	rm -rf $vishead'.ch0.clean'
        rm -rf $vishead'.ch0.clean.fits'
        restor map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' \
               model=$vishead'.10.ch0.model' \
               mode=clean out=$vishead'.ch0.clean'
        fits in=$vishead'.ch0.clean' op=xyout out=$vishead'.ch0.clean.fits'

        rm -rf $vishead'.ch0.residual'
        rm -rf $vishead'.ch0.residual.fits'
        restor map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' \
               model=$vishead'.10.ch0.model' \
               mode=residual out=$vishead'.ch0.residual'
        fits in=$vishead'.ch0.residual' op=xyout out=$vishead'.ch0.residual.fits'

        output=$(python get_rms.py  $rx  $sideband  $target $track)
        IFS='   ' read -r -a array <<< "$output"
        rms=${array[0]}
        cut=$(bc -l <<< "${array[0]}*1.5")
        echo "The obtained rms for $target is ${array[0]} Jy/beam"
        box=${array[1]}','${array[2]}','${array[3]}','${array[4]}
        echo 'boxes('${array[1]}','${array[2]}','${array[3]}','${array[4]}')'

        rm -rf $vishead'.ch0.dirty'
        rm -rf $vishead'.ch0.beam'
        invert vis=$vishead'.cal.miriad' \
               options=systemp,mfs,double robust=2.0 \
               map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' cell=$cellsize imsize=$imsize

        rm -rf $vishead'.ch0.dirty.fits'
        rm -rf $vishead'ch0.beam.fits'
        fits in=$vishead'.ch0.dirty' op=xyout out=$vishead'.ch0.dirty.fits'
        fits in=$vishead'.ch0.beam' op=xyout out=$vishead'.ch0.beam.fits'

	rm -rf $vishead'.ch0.model'
        rm -rf $vishead'.ch0.model.fits'
        clean map=$vishead'.ch0.dirty' \
              beam=$vishead'.ch0.beam' \
              out=$vishead'.ch0.model' cutoff=$cut niters=1000 \
              region='boxes('${array[1]}','${array[2]}','${array[3]}','${array[4]}')' options=positive
        fits in=$vishead'.ch0.model' op=xyout out=$vishead'.ch0.model.fits'

	# restore image
        rm -rf $vishead'.ch0.clean'
        rm -rf $vishead'.ch0.clean.fits'
        restor map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' \
               model=$vishead'.ch0.model' \
               mode=clean out=$vishead'.ch0.clean'
        fits in=$vishead'.ch0.clean' op=xyout out=$vishead'.ch0.clean.fits'

	rm -rf $vishead'.ch0.residual'
        rm -rf $vishead'.ch0.residual.fits'
        restor map=$vishead'.ch0.dirty' \
               beam=$vishead'.ch0.beam' \
               model=$vishead'.ch0.model' \
               mode=residual out=$vishead'.ch0.residual'
        fits in=$vishead'.ch0.residual' op=xyout out=$vishead'.ch0.residual.fits'

        rm -rf $vishead'.ch0.clean.pbcor'
        rm -rf $vishead'.ch0.clean.pbcor.fits'
        linmos in=$vishead'.ch0.clean' out=$vishead'.ch0.clean.pbcor'
        fits in=$vishead'.ch0.clean.pbcor' op=xyout out=$vishead'.ch0.clean.pbcor.fits'

        output=$(python flux_measure.py  $rx  $sideband  $target $track $box $rms)
        IFS='   ' read -r -a array <<< "$output"
        echo "The peak flux of clean map is ${array[0]} mJy/beam"
        echo "The fitted 2D Gaussian component has major and minor FWHM ${array[1]} arcsec and ${array[2]} arcsec"
        echo "The integrated flux density is ${array[3]} mJy"


	# creating self-calibrated image
        rm -rf $vishead'.sel.ch0.dirty'
        rm -rf $vishead'.sel.ch0.beam'
        invert vis=$vishead'.cal.miriad.sel' \
               options=systemp,mfs,double robust=2.0 \
               map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' cell=$cellsize imsize=$imsize
#               select='uvrange(0,80)'

        rm -rf $vishead'.sel.ch0.dirty.fits'
        rm -rf $vishead'.sel.ch0.beam.fits'
        fits in=$vishead'.sel.ch0.dirty' op=xyout out=$vishead'.sel.ch0.dirty.fits'
        fits in=$vishead'.sel.ch0.beam' op=xyout out=$vishead'.sel.ch0.beam.fits'

        rm -rf $vishead'.10.sel.ch0.model'
        rm -rf $vishead'.10.sel.ch0.model.fits'
        clean map=$vishead'.sel.ch0.dirty' \
                beam=$vishead'.sel.ch0.beam' \
                out=$vishead'.10.sel.ch0.model' cutoff=0.01 niters=10 options=positive
        fits in=$vishead'.10.sel.ch0.model' op=xyout out=$vishead'.10.sel.ch0.model.fits'

        rm -rf $vishead'.sel.ch0.clean'
        rm -rf $vishead'.sel.ch0.clean.fits'
        restor map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' \
               model=$vishead'.10.sel.ch0.model' \
               mode=clean out=$vishead'.sel.ch0.clean'
        fits in=$vishead'.sel.ch0.clean' op=xyout out=$vishead'.sel.ch0.clean.fits'

        rm -rf $vishead'.sel.ch0.residual'
        rm -rf $vishead'.sel.ch0.residual.fits'
        restor map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' \
               model=$vishead'.10.sel.ch0.model' \
               mode=residual out=$vishead'.sel.ch0.residual'
        fits in=$vishead'.sel.ch0.residual' op=xyout out=$vishead'.sel.ch0.residual.fits'
        
        output=$(python get_rms.sel.py  $rx  $sideband  $target $track)
        IFS='   ' read -r -a array <<< "$output"
        cut=$(bc -l <<< "${array[0]}*1.5")
        rms=${array[0]}
	echo "The obtained rms for $target is ${array[0]} Jy/beam"
	box=${array[1]}','${array[2]}','${array[3]}','${array[4]}
        echo 'boxes('${array[1]}','${array[2]}','${array[3]}','${array[4]}')'

        rm -rf $vishead'.sel.ch0.dirty'
        rm -rf $vishead'.sel.ch0.beam'
        invert vis=$vishead'.cal.miriad.sel' \
               options=systemp,mfs,double robust=2.0 \
               map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' cell=$cellsize imsize=$imsize

        rm -rf $vishead'.sel.ch0.dirty.fits'
        rm -rf $vishead'sel.ch0.beam.fits'
        fits in=$vishead'.sel.ch0.dirty' op=xyout out=$vishead'.sel.ch0.dirty.fits'
        fits in=$vishead'.sel.ch0.beam' op=xyout out=$vishead'.sel.ch0.beam.fits'

        rm -rf $vishead'.sel.ch0.model'
        rm -rf $vishead'.sel.ch0.model.fits'
        clean map=$vishead'.sel.ch0.dirty' \
              beam=$vishead'.sel.ch0.beam' \
              out=$vishead'.sel.ch0.model' cutoff=$cut niters=1000 \
              region='boxes('${array[1]}','${array[2]}','${array[3]}','${array[4]}')' options=positive
        fits in=$vishead'.sel.ch0.model' op=xyout out=$vishead'.sel.ch0.model.fits'

        # restore image
        rm -rf $vishead'.sel.ch0.clean'
        rm -rf $vishead'.sel.ch0.clean.fits'
        restor map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' \
               model=$vishead'.sel.ch0.model' \
               mode=clean out=$vishead'.sel.ch0.clean'
        fits in=$vishead'.sel.ch0.clean' op=xyout out=$vishead'.sel.ch0.clean.fits'

        rm -rf $vishead'.sel.ch0.residual'
        rm -rf $vishead'.sel.ch0.residual.fits'
        restor map=$vishead'.sel.ch0.dirty' \
               beam=$vishead'.sel.ch0.beam' \
               model=$vishead'.sel.ch0.model' \
               mode=residual out=$vishead'.sel.ch0.residual'
        fits in=$vishead'.sel.ch0.residual' op=xyout out=$vishead'.sel.ch0.residual.fits'

        rm -rf $vishead'.sel.ch0.clean.pbcor'
        rm -rf $vishead'.sel.ch0.clean.pbcor.fits'
        linmos in=$vishead'.sel.ch0.clean' out=$vishead'.sel.ch0.clean.pbcor'
        fits in=$vishead'.sel.ch0.clean.pbcor' op=xyout out=$vishead'.sel.ch0.clean.pbcor.fits'


        output=$(python flux_measure.sel.py  $rx  $sideband  $target $track $box $rms)
        IFS='   ' read -r -a array <<< "$output"
        echo "The peak flux of clean map is ${array[0]} mJy/beam"
        echo "The fitted 2D Gaussian component has major and minor FWHM ${array[1]} arcsec and ${array[2]} arcsec"
        echo "The integrated flux density is ${array[3]} mJy"



        # collecting self-calibrated visibilities into a folder
        mv *.sel ./selcal_Miriad

        # collecting solution tables into the folder
        mv *.gain ./selcal_Miriad
        mv *.gain.txt ./selcal_Miriad

      done
    done
  done
done

mv *.pdf ./fitting_img

