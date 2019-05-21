# Runs dos to unix and cleans empty csv lines
find . -name "*.csv" | while read line; do
	# translate from dos to unix
	dos2unix $line
	# remove empty lines
	sed -i '' '/^\( *, *\)*$/d' $line
done
