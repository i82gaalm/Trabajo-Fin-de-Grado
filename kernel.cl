__kernel void ctm(__global const uchar *img, __global unsigned char *agujero, __global unsigned char *serrin, __global int *pixels_serrin, __global int *pixels, int rows, int cols, 
    __global const int max_agujero[3], __global const int min_agujero[3], __global const int min_serrin[3], __global const int max_serrin[3]) {

    int i = get_global_id(0);
    int j = get_global_id(1);
    
    int aux = (i * cols + j) * 3;

    uchar blue = img[aux];
    uchar green = img[aux + 1];
    uchar red = img[aux + 2];
    
    atomic_inc(pixels);

    if(red >= min_agujero[0] && green >= min_agujero[1] && blue >= min_agujero[2]){
        if(red <= max_agujero[0] && green <= max_agujero[1] && blue <= max_agujero[2]){
            agujero[i * cols + j] = 255;
        }    
    }

    if(red >= min_serrin[0] && green >= min_serrin[1] && blue >= min_serrin[2]){
        if(red <= max_serrin[0] && green <= max_serrin[1] && blue <= max_serrin[2]){
            serrin[i * cols + j] = 255;
            atomic_inc(pixels_serrin);
        }    
    }

}