#include <stdio.h>
#include <fstream>
#include <algorithm>
#include <iostream>
#include <string.h>
#include <string>
using namespace std;
class OBJ{
private:
    string name;
    string num;
    int dec;
public:
    OBJ(){
    }
    OBJ(const char *_n,const char *nn){
        name=_n;
        dec=0;
        for(int i=0;nn[i];i++){
            dec=dec*2+nn[i]-'0';
        }
    }
    string get_name(){
        return name;
    }
    int get_num(){
        return dec;
    }
    bool operator < (const OBJ &n)const{
        return n.dec>dec;
    }
};
int main(){
    FILE *f=fopen("input.txt","r");
    char name[100],num[100];
    OBJ obj[100];
    int cnt=0;
    while(~fscanf(f,"%s %s",name,num)){
        obj[cnt++]=OBJ(name,num); 
    }
    sort(obj,obj+cnt);
    FILE *fo=fopen("output.txt","w");
    for(int i=0;i<cnt;i++){
        fprintf(fo,"%s %d\n",obj[i].get_name().c_str(),obj[i].get_num());
    }
    fclose(f);
    fclose(fo);

    return 0;
}
