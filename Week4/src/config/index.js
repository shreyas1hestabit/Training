import dotenv from "dotenv"; //is library ka kaam hai .env ko memory me load krna.
import path from "path"; //node ka built-in module which is used to create files ka correct absolute path
//enviornment path ko identify kra rhe hai
const env = process.env.NODE_ENV || "local"; //node ka enviornment check kr rhe hai and agr kuch bh set nh hai toh set it to local.abh hm locally operate kr rhe hai toh isk baad .env.local load hoga.
//yeh core part hai
dotenv.config({ // file ko read + load, now konsi file ko load read krna will be told by next code line
    path: path.resolve(process.cwd(), `.env.${env}`) //process.cwd()---> project root and .env.${env}---->.env.local
    //iss line k baad hmare process k environment ka port will be set to 3000 qk woh port hmne .env.local mein define kiya hai. agr koi or port suppose 8080 define kiya hota toh woh use ho jata.
});

//this set of code is used qk direct process.env use nhi krte coz we want ki sab configs ek jgh se export ho. 
//this is a must to follow rule k configs should be centralized 
export const config={
    env,
    port:process.env.PORT
};