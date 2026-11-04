#!/usr/bin/env Rscript
# Reproducible RDA of the supplied shading experiment; R is the sole graphics backend.
# Run from this delivery folder: Rscript analysis.R
suppressPackageStartupMessages({library(vegan); library(permute); library(readxl)
  library(ggplot2); library(ggrepel); library(ragg)})
options(stringsAsFactors = FALSE, digits = 10)
set.seed(20261021)
for (d in c('data','statistics','figures','qa')) dir.create(d, showWarnings=FALSE)
csv <- function(x, f, rows=FALSE) write.csv(x, file.path('statistics', f), row.names=rows, na='')
raw <- as.data.frame(read_excel('original/RDA.xlsx', sheet=1, .name_repair='minimal'))
raw <- raw[!is.na(raw[[2]]), , drop=FALSE]
stopifnot(ncol(raw)==22, nrow(raw)==15)
original_names <- names(raw)
nm <- c('group_header','sample_id','Light','AirTemp','RH','SoilTemp','SoilMoist','BranchTemp',
        'TRL','RSA','ARD','TN','TP','TK','CAT','MDA','SOD','POD','Rubisco','Pollen','Yield','FSR')
names(raw) <- nm
d <- raw
d$treatment <- factor(ifelse(grepl('^CK', d$sample_id),'CK',sub('%.*','%',d$sample_id)),
                      levels=c('CK','35%','50%','65%','80%'))
d$shade_percent <- c(CK=0,'35%'=35,'50%'=50,'65%'=65,'80%'=80)[as.character(d$treatment)]
stopifnot(!anyNA(d$treatment), !anyDuplicated(d$sample_id), all(table(d$treatment)==3))
xnames <- c('Light','AirTemp','RH','SoilTemp','SoilMoist','BranchTemp')
ynames <- nm[9:22]
for(v in c(xnames,ynames)) {d[[v]] <- as.numeric(d[[v]]); stopifnot(all(is.finite(d[[v]])), sd(d[[v]])>0)}
stopifnot(all(as.matrix(d[,c(xnames,ynames)])>0))
X <- d[,xnames]; Yraw <- as.matrix(d[,ynames]); rownames(Yraw) <- d$sample_id
Y <- scale(Yraw); rownames(X) <- d$sample_id
write.csv(d[,c('sample_id','treatment','shade_percent',xnames,ynames)],'data/analysis_data.csv',row.names=FALSE)
write.csv(Y,'data/standardized_responses.csv',row.names=TRUE)
labels <- c(Light='Light intensity', AirTemp='Air temperature', RH='Relative humidity',
 SoilTemp='Soil temperature',SoilMoist='Soil moisture',BranchTemp='Branch surface temperature',
 TRL='Total root length',RSA='Root surface area',ARD='Average root diameter',TN='Branch tissue total nitrogen',
 TP='Branch tissue total phosphorus',TK='Branch tissue total potassium',CAT='Catalase (CAT)',MDA='Malondialdehyde (MDA)',
 SOD='Superoxide dismutase (SOD)',POD='Peroxidase (POD)',Rubisco='Rubisco activity',Pollen='Pollen viability',
 Yield='Cumulative fruit yield',FSR='Fruit set rate')
dict <- data.frame(original_header=original_names[3:22],code=nm[3:22],english=unname(labels[nm[3:22]]),
 role=c(rep('Environmental predictor candidate',6),rep('Plant response (TN/TP/TK: branch tissue)',14)),
 units='Not supplied; not inferred')
write.csv(dict,'data/variable_dictionary.csv',row.names=FALSE)
csv(data.frame(variable=c(xnames,ynames),n=sapply(d[,c(xnames,ynames)],length),missing=0,
 min=sapply(d[,c(xnames,ynames)],min),max=sapply(d[,c(xnames,ynames)],max),
 mean=sapply(d[,c(xnames,ynames)],mean),sd=sapply(d[,c(xnames,ynames)],sd)), 'data_quality.csv')
csv(as.data.frame(table(d$treatment)), 'sample_counts.csv')
csv(cor(X), 'environment_correlations.csv',TRUE)
csv(cor(Yraw), 'response_correlations.csv',TRUE)
# Flag, never delete, univariate observations outside 1.5 IQR fences.
flags <- do.call(rbind,lapply(c(xnames,ynames),function(v){q<-quantile(d[[v]],c(.25,.75));
 ii<-which(d[[v]]<q[1]-1.5*diff(q)|d[[v]]>q[2]+1.5*diff(q));
 if(!length(ii))return(NULL); data.frame(sample_id=d$sample_id[ii],variable=v,value=d[[v]][ii],action='Retained')}))
csv(flags,'iqr_flags_retained.csv')
# Outcome-independent selection: light first, then a physically distinct soil variable;
# reject candidates with absolute correlation >= 0.90 against any retained predictor. No p-value selection.
priority <- c('Light','SoilTemp','AirTemp','RH','SoilMoist','BranchTemp')
keep <- character(); selection <- data.frame()
for(v in priority) {
 mx <- if(length(keep)) max(abs(cor(X[[v]],X[,keep,drop=FALSE]))) else 0
 retain <- mx < .90
 selection <- rbind(selection,data.frame(variable=v,max_abs_r_with_retained=mx,
                    decision=if(retain)'Retain' else 'Exclude: redundant (|r| >= 0.90)'))
 if(retain) keep<-c(keep,v)
}
stopifnot(length(keep)<=floor((nrow(d)-1)/5), identical(keep,c('Light','SoilTemp')))
csv(selection,'variable_selection.csv')
# RCBD metadata must be supplied by experimental records, never inferred from IDs.
mapping_path <- 'data/block_map.csv'
if(!file.exists(mapping_path)) write.csv(data.frame(sample_id=d$sample_id,block=NA_character_),mapping_path,row.names=FALSE,na='')
mapping <- read.csv(mapping_path,colClasses='character')
stopifnot(!anyDuplicated(mapping$sample_id),setequal(mapping$sample_id,d$sample_id))
block <- mapping$block[match(d$sample_id,mapping$sample_id)]
block_ok <- all(!is.na(block)&nzchar(trimws(block)))
if(any(!is.na(block)&nzchar(trimws(block)))&&!block_ok) stop('Incomplete block map: fill every sample or leave all blank.')
if(block_ok) {
 block <- factor(block)
 stopifnot(nlevels(block)==3,all(table(block)==5),all(table(block,d$treatment)==1))
}
fit_rda <- function(y,rhs,ed) {
 if(block_ok) ed$Block <- block
 f <- as.formula(paste('y ~',rhs,if(block_ok)'+ Condition(Block)' else ''))
 rda(f,data=ed)
}
primary <- fit_rda(Y,'Light + SoilTemp',X)
full <- fit_rda(Y,paste(xnames,collapse='+'),X)
stopifnot(max(vif.cca(primary))<5, primary$CA$rank>0)
csv(data.frame(variable=names(vif.cca(full)),VIF=unname(vif.cca(full))),'VIF_all_six.csv')
csv(data.frame(variable=names(vif.cca(primary)),VIF=unname(vif.cca(primary))),'VIF_primary.csv')
B <- 9999L
P <- if(block_ok) shuffleSet(nrow(Y),nset=B,control=how(nperm=B,blocks=block)) else matrix(rep(seq_len(nrow(Y)),2),nrow=2,byrow=TRUE) # identity only: compute F, discard all nominal P values
if(!block_ok && file.exists('statistics/permutation_matrix.rds')) unlink('statistics/permutation_matrix.rds')
if(block_ok) saveRDS(P,'statistics/permutation_matrix.rds')
test_rda <- function(m,by=NULL) {
 a <- anova(m,by=by,permutations=P)
 if(!block_ok) a$`Pr(>F)` <- NA_real_
 a$inference_status <- if(block_ok)'RCBD: Block conditioned, within-block permutations' else 'NOT TESTED: actual block membership unavailable'
 a
}
csv(data.frame(block_mapping_confirmed=block_ok,permutations=if(block_ok)B else 0,
 inference=if(block_ok)'Partial RDA: Condition(Block); 9999 within-block residual permutations' else
 'Exploratory unconditioned RDA only; no valid RCBD P values reported'), 'inference_status.csv')
global <- test_rda(primary)
axes <- test_rda(primary,by='axis')
marg <- test_rda(primary,by='margin')
marg$P_BH <- p.adjust(marg$`Pr(>F)`,method='BH')
csv(global,'primary_global_permutation.csv',TRUE)
csv(axes,'primary_axis_permutations.csv',TRUE)
csv(marg,'primary_marginal_permutations_BH.csv',TRUE)
csv(test_rda(primary,by='terms'),'primary_sequential_terms_order_dependent.csv',TRUE)
rs <- RsquareAdj(primary)
eig <- eigenvals(primary,model='all')
axes_tab <- data.frame(axis=names(eig),eigenvalue=as.numeric(eig),
 percent_total=100*eig/primary$tot.chi,
 percent_constrained=ifelse(grepl('^RDA',names(eig)),100*eig/primary$CCA$tot.chi,NA))
csv(axes_tab,'ordination_eigenvalues.csv')
single <- do.call(rbind,lapply(xnames,function(v){m<-fit_rda(Y,v,X);a<-test_rda(m)
 data.frame(variable=v,R2=RsquareAdj(m)$r.squared,adj_R2=RsquareAdj(m)$adj.r.squared,
 F=a$F[1],p=a$`Pr(>F)`[1])}))
single$p_BH <- p.adjust(single$p,'BH');csv(single,'exploratory_single_predictors_BH.csv')
# PCA sensitivity uses the same six standardized predictors, not response information.
pc <- prcomp(X,scale.=TRUE)
pcdf <- data.frame(EnvPC1=pc$x[,1],EnvPC2=pc$x[,2])
pcmodel <- fit_rda(Y,'EnvPC1+EnvPC2',pcdf)
csv(data.frame(variable=rownames(pc$rotation),pc$rotation),'environment_PCA_loadings.csv')
csv(data.frame(axis=paste0('EnvPC',1:6),percent=100*pc$sdev^2/sum(pc$sdev^2)), 'environment_PCA_variance.csv')
group_data <- data.frame(Treatment=d$treatment)
group_model <- fit_rda(Y,'Treatment',group_data)
partial <- fit_rda(Y,'Light+SoilTemp+Condition(Treatment)',cbind(X,group_data))
no_nutrients <- fit_rda(Y[,!colnames(Y)%in%c('TN','TP','TK')],'Light+SoilTemp',X)
log_model <- fit_rda(scale(log(Yraw)),'Light+SoilTemp',X)
models <- list(primary=primary,all_six=full,environment_PC1_PC2=pcmodel,treatment_factor=group_model,
               conditional_on_treatment=partial,without_TN_TP_TK=no_nutrients,log_responses=log_model)
model_table <- do.call(rbind,lapply(names(models),function(k){m<-models[[k]];a<-test_rda(m)
 data.frame(model=k,constraint_df=m$CCA$qrank,residual_df=tail(a$Df,1),R2=RsquareAdj(m)$r.squared,
 adjusted_R2=RsquareAdj(m)$adj.r.squared,F=a$F[1],p=a$`Pr(>F)`[1])}))
csv(model_table,'model_comparisons_sensitivity.csv')
# Out-of-sample Q2: each held-out fold uses training response means and SDs;
# held-out residuals are compared with a training-mean-only prediction.
cv <- function(x, folds) {
 err <- base <- 0; foldtab <- data.frame()
 for(f in unique(folds)) {
  te<-which(folds==f);tr<-which(folds!=f)
  mu<-colMeans(Yraw[tr,,drop=FALSE]);s<-apply(Yraw[tr,,drop=FALSE],2,sd)
  ytr<-sweep(sweep(Yraw[tr,,drop=FALSE],2,mu),2,s,'/')
  yte<-sweep(sweep(Yraw[te,,drop=FALSE],2,mu),2,s,'/')
  fit<-lm.fit(cbind(Intercept=1,as.matrix(x[tr,,drop=FALSE])),ytr)
  pred<-cbind(1,as.matrix(x[te,,drop=FALSE]))%*%fit$coefficients
  se<-sum((yte-pred)^2);ss<-sum(yte^2);err<-err+se;base<-base+ss
  foldtab<-rbind(foldtab,data.frame(fold=as.character(f),test_samples=paste(d$sample_id[te],collapse=';'),
                                 squared_error=se,baseline_error=ss))
 }
 list(Q2=1-err/base,folds=foldtab)
}
cvrows<-data.frame()
for(k in c('primary','all_six'))for(kind in c('leave_one_row_out','leave_one_treatment_out')) {
 x<-if(k=='primary')X[,keep] else X
 folds<-if(kind=='leave_one_row_out')seq_len(nrow(d)) else d$treatment
 out<-cv(x,folds);cvrows<-rbind(cvrows,data.frame(model=k,validation=kind,Q2=out$Q2))
 csv(out$folds,paste0('CV_',k,'_',kind,'.csv'))
}
csv(cvrows,'cross_validation_Q2.csv')
loo<-do.call(rbind,lapply(seq_len(nrow(d)),function(i){m<-rda(Y[-i,]~Light+SoilTemp,data=X[-i,]);
 data.frame(omitted=d$sample_id[i],R2=RsquareAdj(m)$r.squared,adjusted_R2=RsquareAdj(m)$adj.r.squared)}))
csv(loo,'leave_one_row_out_fit_sensitivity.csv')
lmfit<-lm(Y~Light+SoilTemp,data=X)
csv(data.frame(sample_id=d$sample_id,leverage=hatvalues(lmfit),
 standardized_multivariate_residual_norm=sqrt(rowSums(residuals(lmfit)^2)),
 leverage_flag=hatvalues(lmfit)>2*3/nrow(d)),'influence_diagnostics.csv')
# Multivariate dispersion is supplementary for interpreting treatment grouping.
disp<-betadisper(dist(Y),d$treatment,type='median',bias.adjust=TRUE)
if(block_ok) csv(permutest(disp,permutations=P)$tab,'treatment_dispersion_permutation.csv',TRUE) else csv(data.frame(status='Not tested: RCBD block membership unavailable'),'treatment_dispersion_permutation.csv')
sc<-scores(primary,choices=1:2,display=c('sites','species','bp'),scaling=2)
sites<-data.frame(sample_id=d$sample_id,treatment=d$treatment,sc$sites)
traits<-data.frame(code=rownames(sc$species),sc$species)
env<-data.frame(code=rownames(sc$biplot),sc$biplot)
csv(sites,'figure_site_scores_scaling2.csv');csv(traits,'figure_response_scores_scaling2.csv');csv(env,'figure_environment_scores_scaling2.csv')
saveRDS(models,'statistics/fitted_models.rds')
capture.output(sessionInfo(),file='statistics/R_sessionInfo.txt')
capture.output({cat('PRIMARY RDA\n');print(summary(primary));print(global);print(axes);print(marg)
 cat('\nSENSITIVITY MODELS\n');print(model_table);cat('\nCROSS-VALIDATION\n');print(cvrows)
 cat('\nENVIRONMENT PCA\n');print(summary(pc));cat('\nSAMPLE TREATMENT COUNTS\n');print(table(d$treatment))},
 file='statistics/full_statistical_output.txt')
# Figure contract: a single quantitative ordination, exploratory association, no causal claim.
# All 15 rows and 14 responses shown; no n=3 confidence ellipses. Scaling=2.
# Neutral arrows: responses; vermilion arrows: retained environmental constraints.
# Arrow scores use one shared multiplier=2.2 (no independent rescaling).
pal<-c('CK'='#505050','35%'='#0072B2','50%'='#009E73','65%'='#CC79A7','80%'='#D55E00')
shapes<-c('CK'=16,'35%'=17,'50%'=15,'65%'=18,'80%'=8)
trait_labels<-c(TRL='TRL',RSA='RSA',ARD='ARD',TN='TN',TP='TP',TK='TK',CAT='CAT',MDA='MDA',SOD='SOD',
 POD='POD',Rubisco='Rubisco',Pollen='Pollen',Yield='Yield',FSR='Fruit set')
traits$label<-unname(trait_labels[traits$code]);env$label<-unname(labels[env$code])
# A single shared factor preserves relative arrow lengths.
traits[,c('RDA1','RDA2')]<-traits[,c('RDA1','RDA2')]*2.2
env[,c('RDA1','RDA2')]<-env[,c('RDA1','RDA2')]*2.2
label_data<-rbind(data.frame(traits,ink='#444444',weight='plain'),data.frame(env,ink='#B44A24',weight='bold'),
 data.frame(code=sites$sample_id,RDA1=sites$RDA1,RDA2=sites$RDA2,label='',ink='#444444',weight='plain'))
# Label positions change annotation only, never scores or arrow geometry.
targets<-data.frame(code=c('TRL','RSA','ARD','TN','TP','TK','CAT','MDA','SOD','POD','Rubisco','Pollen','Yield','FSR','Light','SoilTemp'),
 tx=c(.35,-.4,-.5,1.25,2.1,-.85,.2,-2.0,1.8,.9,2.75,2.7,2.35,1.65,-2.55,-2.25),
 ty=c(-1.45,-.85,1.35,1.6,.07,.35,.8,-.5,.95,-1.05,-.3,.55,-1.15,-.75,.35,-1.55))
ii<-match(label_data$code,targets$code)
label_data$nx<-ifelse(is.na(ii),0,targets$tx[ii]-label_data$RDA1)
label_data$ny<-ifelse(is.na(ii),0,targets$ty[ii]-label_data$RDA2)
xr<-range(c(sites$RDA1,traits$RDA1,env$RDA1));yr<-range(c(sites$RDA2,traits$RDA2,env$RDA2))
pad<-max(diff(xr),diff(yr))*.20
p<-ggplot()+
 geom_segment(data=traits,aes(x=0,y=0,xend=RDA1,yend=RDA2),colour='#777777',linewidth=.27,
              arrow=grid::arrow(length=grid::unit(1.4,'mm'),type='closed'))+
 geom_segment(data=env,aes(x=0,y=0,xend=RDA1,yend=RDA2),colour='#B44A24',linewidth=.55,
              arrow=grid::arrow(length=grid::unit(2.1,'mm'),type='closed'))+
 geom_point(data=sites,aes(RDA1,RDA2,colour=treatment,shape=treatment),size=2.5,stroke=.65)+
 geom_text_repel(data=label_data,aes(RDA1,RDA2,label=label,fontface=weight),
                 colour=label_data$ink,seed=241,size=2.7,family='Liberation Sans',
                 max.overlaps=Inf,box.padding=.6,point.padding=.4,
                 min.segment.length=0,segment.colour='#AAAAAA',segment.size=.18,
                 nudge_x=label_data$nx,nudge_y=label_data$ny,force=.03,max.time=Inf,max.iter=50000)+
 scale_colour_manual(values=pal,labels=c('CK (0%)','35%','50%','65%','80%'))+
 scale_shape_manual(values=shapes,labels=c('CK (0%)','35%','50%','65%','80%'))+
 coord_fixed(xlim=xr+c(-pad,pad),ylim=yr+c(-pad,pad),clip='on')+
 labs(x=sprintf('RDA1 (%.1f%% of total variance)',axes_tab$percent_total[1]),
      y=sprintf('RDA2 (%.1f%% of total variance)',axes_tab$percent_total[2]),
      colour='Shading',shape='Shading',
      subtitle=if(block_ok)sprintf('Partial RDA; adjusted R² = %.3f; within-block P = %.4f',rs$adj.r.squared,global$`Pr(>F)`[1]) else
        sprintf('Exploratory RDA; adjusted R² = %.3f; block mapping pending',rs$adj.r.squared))+
 theme_classic(base_size=8.5,base_family='Liberation Sans')+
 theme(axis.line=element_line(linewidth=.35),axis.ticks=element_line(linewidth=.3),
       axis.text=element_text(size=7.5,colour='black'),axis.title=element_text(size=8.5),
       legend.position='bottom',legend.title=element_text(size=8),legend.text=element_text(size=8),
       legend.key.width=grid::unit(7,'mm'),legend.margin=margin(t=2),
       plot.subtitle=element_text(size=8.2,margin=margin(b=9)),
       plot.margin=margin(9,11,7,9),panel.grid=element_blank())
# PDF has embedded editable text; TIFF uses lossless LZW compression, 600 dpi, white background.
width_mm<-183;height_mm<-160
w<-width_mm/25.4;h<-height_mm/25.4
svglite::svglite('figures/RDA_shading.svg',width=w,height=h,bg='white')
print(p);invisible(dev.off())
grDevices::cairo_pdf('figures/RDA_shading.pdf',width=w,height=h,family='Liberation Sans',bg='white')
print(p);invisible(dev.off())
ragg::agg_tiff('figures/RDA_shading_600dpi.tiff',width=w,height=h,units='in',res=600,compression='lzw',background='white')
print(p);invisible(dev.off())
ragg::agg_png('figures/RDA_shading_preview.png',width=w,height=h,units='in',res=300,background='white')
print(p);invisible(dev.off())
saveRDS(p,'statistics/figure_ggplot.rds')
cat('Completed analysis and R-only PDF/TIFF/PNG exports.\n')
