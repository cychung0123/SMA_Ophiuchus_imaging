config="com"
flagval="f"

targets='DoAr_16 DoAr_33 YLW_8 GSS_39 DoAr_24E AS_206 GSS_26 WSB_31 VSSG_1 DoAr_25 IRS_37 IRS_41 IRS_51 IRS_39 YLW_47 WSB_60 HBC_266 DoAr_44'
tracks='track1'
sidebands='lsb usb'
rxs='rx345 rx400'

rm -rf *.txt
rm -rf *.rx*
rm -rf ch0
mkdir ch0
cp ../center_track2_2.txt .

for track in $tracks
do
#  cd ch0/
#  rm -rf $track
#  mkdir $track
#  cd ../
  
  for rx in $rxs
  do
      for sideband in $sidebands
      do
        if [ $track = 'track1' ]
	then
		cellsize=0.06
		imsize=512
	fi
	
	for target in $targets
	do
	  
	  datadir='./cal/'
	  vis=$target'.'$rx'.'$sideband'.'$track'.cal.miriad'
	  cp -r $datadir$vis ./

	  vishead=$target'.'$rx'.'$sideband'.'$track

	  uvflag vis=$vishead'.cal.miriad' edge=64,64,0 flagval=$flagval
#	  rm -rf $vishead'.ch0.miriad'
#	  uvaver vis=$vishead'.cal.miriad' \
#	       out=$vishead'.ch0.miriad' \
#	       line='channel,1,1,1024,1' options='nocal,nopass,nopol'

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
#                  select='uvrange(0,80)'

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

          # creating non-self-calibrated image
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


	  mv *.ch0.beam ./ch0
	  mv *.ch0.model ./ch0
	  mv *.ch0.clean ./ch0
	  mv *.ch0.clean.pbcor ./ch0
	  mv *.ch0.dirty ./ch0
	  mv *.ch0.residual ./ch0
	  mv *.ch0.*.fits ./ch0
	  rm -rf *.miriad
        done
      done
  done
done

cp *.txt ./ch0
cp flux_track* ../SED/
cp rms_track* ../SED/
rm *.txt

rm -rf fitting_img
mkdir fitting_img
mv *.pdf ./fitting_img

cd ch0
cp ../plot_clean_image.py .
echo $(python plot_clean_image.py)
cp *post* ../
