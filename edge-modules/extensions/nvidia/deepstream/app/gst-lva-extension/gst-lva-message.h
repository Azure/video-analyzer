
#ifndef __GST_LVA_MESSAGE_H__
#define __GST_LVA_MESSAGE_H__
 
#include <gst/gst.h>

#define GST_LVA_MESSAGE_META_TYPE       (gst_lva_message_api_get_type())
#define GST_LVA_MESSAGE_META_IMPL_NAME   "GstLVAMessageMeta"
#define GST_LVA_MESSAGE_META_TAG         "gst_lva_message_meta"
#define GST_LVA_MESSAGE_META_API_NAME    "GstLVAMessageMetaAPI"


typedef struct _GstLVAMessageMeta       GstLVAMessageMeta;
typedef struct _GstLVAMessage    GstLVAMessage    ; 


struct _GstLVAMessage {     
    guint64 sequence_number;    
    guint64 timestamp;    
};

struct _GstLVAMessageMeta {
    GstMeta          gstMeta;  
    GstLVAMessage    message;
};  



GType gst_lva_message_api_get_type(void);

const GstMetaInfo *gst_lva_message_meta_get_info(void);
 
GstLVAMessageMeta* gst_lva_buffer_add_message( GstBuffer *buffer, GstLVAMessage *gstlvaMsg);

gboolean gst_lva_buffer_remove_message(GstBuffer *buffer);

GstLVAMessage *gst_lva_buffer_get_message(GstBuffer *buffer);
 

#endif 