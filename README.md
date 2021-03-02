
##  Throttle me

## Control the pulce 

## Screen

h/w
https://www.winstar.com.tw/products/oled-module/graphic-oled-display/4-pin-oled.html



Font to bitmap

1. Install Fontforge
2. Load Font (any TTF)
3. Double-click a digit
4. Select menu : 'Element' -> Bitmap Strike Avaiable
  - selct pixel size 
	62 => (22/36)
	70 => (32/52)

5. Select menu: 'View' -> '70 Pixel bitmap'

6. Double-click a digit
 - select 'file' -> 'export'
   'format' 'C FontForge'

7. Copy the data[] inside the empty array below (replace <data>)


    ```
    x = [<data>]
    console.log('b"' + x.map(x =>  '\\x'+ ("00" + (255-x).toString(16)).substr(-2)).join('') + '"')
    ```

8. Take the output, and Add line in Python (replace <data>)
    ```
    char0 = bytearray(<data>)
