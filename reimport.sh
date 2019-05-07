for file in $(find Assets/Resources -name "*.meta") ; do
	rm -rf $file
done
