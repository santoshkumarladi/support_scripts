This repo contains support scripts for setting up FIT clusters 
Mainly the scripts are divded into 3 categories 
1. Setup the cluster or config like
   -> Setting up archive on the cluster for log backup.
   -> Creating the conatiners with different properties.
   -> Uploading golen imgaes for io
2. Workload or scenario
   -> Multiple scripts to simulate different use case's
   -> Vm lifcycle , clone lifeccycle , Snapshot's lifecycle , DR Lifecycle , Storage Policies
   -> PC support scripts for setting up DR , Stroage Policy 
3. EI simulator scripts
   -> Disk EI ( offline/online , fail disk , Remove / Add disk )
   -> Process EI ( selected porcess provided by user or pickup any random process from the cluster)
   -> CVM / Host EI ( powe cycle )
   -> Network EI ( Inject latencies / bring down port)
