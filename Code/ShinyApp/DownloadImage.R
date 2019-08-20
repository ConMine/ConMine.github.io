require(WikipediR); require(rvest)

#titles= vector of page name(s)
#res= desired width in pixels (220 px thumbnail by default)
#savedest= save destination (w terminal '/'); wd by default

getwikipic<-function(title){
    d<-page_info("en","wikipedia",page=title,clean_response=T)
    url<-d[[1]]$fullurl
    wikipage<-html_session(url)
    imginfo<-wikipage %>% html_nodes("tr:nth-child(2) img")
    img.url<- imginfo[1] %>% html_attr("src")
    if(is_empty(img.url)){
      return(NA)
    }else{
      img.url<-paste0("https:",img.url)
      return(img.url)#End lapply
    }
}#End function
