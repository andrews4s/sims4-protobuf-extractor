import io
import os

import sys

import google
import sims4


@sims4.commands.Command('proto', command_type=sims4.commands.CommandType.Live)
def proto(_connection=None):
    def decompile_descriptor(dc, output_path, pb_module):
        from google.protobuf.descriptor_pb2 import FileDescriptorProto
        from google.protobuf.descriptor import FileDescriptor
        assert isinstance(pb_module, FileDescriptor)
        pb = FileDescriptorProto()
        pb_module.CopyToProto(pb)
        sci = pb.source_code_info
        from google.protobuf.descriptor_pb2 import SourceCodeInfo
        assert isinstance(sci, SourceCodeInfo)
        src = pb.SerializeToString()
        print(pb_module.name)
        print(src)
        bin_path = os.path.normpath(os.path.join( output_path, pb_module.name + '.bin'))
        text_path = os.path.normpath(os.path.join(output_path,  pb_module.name))
        print(bin_path)
        os.makedirs(os.path.dirname(bin_path), exist_ok=True)
        with io.open(bin_path, 'wb') as f:
            f.write(src)
        with io.open(bin_path, 'rb') as f:
            dc.decompile(f, output_path)
        os.unlink(bin_path)
        pass
    output = sims4.commands.CheatOutput(_connection)
    output('decompiling!')
    import protocolbuffers
    import inspect
    from protocolbuffers.LotTemplate_pb2 import LotObjectList
    from protocolbuffers import \
    Animation_pb2,Area_pb2,Audio_pb2, \
    BuildBuy_pb2,Business_pb2, \
    ChunkHeaders_pb2, ChunkPersistence_pb2,Clubs_pb2,Commands_pb2,Commodities_pb2,Consts_pb2,\
    DebugVisualization_pb2,Dialog_pb2,Distributor_pb2,DistributorOps_pb2,\
    Exchange_pb2,FileSerialization_pb2,\
    GameplaySaveData_pb2,InteractionOps_pb2,\
    Localization_pb2,Loot_pb2,Lot_pb2,LotTemplate_pb2,\
    Math_pb2,Memories_pb2,MoveInMoveOut_pb2,MTXCatalog_pb2,MTXEntitlement_pb2,\
    Outfits_pb2,PersistenceBlobs_pb2,PersistenceControl_pb2,\
    ResourceKey_pb2,Restaurant_pb2,RestApi_pb2,Roommates_pb2,Routing_pb2,S4Common_pb2,\
    SimObjectAttributes_pb2,Sims_pb2,SimsCustomOptions_pb2,\
    SituationPersistence_pb2,Situations_pb2,Social_pb2,Sparse_pb2,Telemetry_pb2,UI_pb2,\
    UMMessage_pb2,\
    LiveEvent_pb2,\
    Rewards_pb2,\
    VFX_pb2, WeatherSeasons_pb2, Venue_pb2, Vehicles_pb2
    from protocolbuffers.ChunkHeaders_pb2 import BlueprintThumbnailChunkPackageHeader
    
    output('importing done')
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", "ProtocolBuffers")
    os.makedirs(output_path, exist_ok=True)
    modules = inspect.getmembers(protocolbuffers)
    dc = ProtobinDecompiler()
    decompile_descriptor(dc,output_path,google.protobuf.descriptor_pb2.DESCRIPTOR)
    for mod in modules:
        pb_obj = eval('protocolbuffers.'+ str(mod[0]))
        if hasattr(pb_obj, 'DESCRIPTOR'):
            output('decompiling ' + str(mod[0]))
            pb_module = eval('protocolbuffers.' + str(mod[0]) + '.DESCRIPTOR')
            decompile_descriptor(dc, output_path, pb_module)
    output('Done!')

import google.protobuf.descriptor_pb2 as pb2

#From https://github.com/fry/d3/blob/master/decompile_protobins.py
class ProtobinDecompiler:
    proto3 = False
    label_map = {
        pb2.FieldDescriptorProto.LABEL_OPTIONAL: "optional",
        pb2.FieldDescriptorProto.LABEL_REQUIRED: "required",
        pb2.FieldDescriptorProto.LABEL_REPEATED: "repeated"
    }    
    extension_label_map = {
        pb2.FieldDescriptorProto.LABEL_OPTIONAL: "optional",
        pb2.FieldDescriptorProto.LABEL_REQUIRED: "optional",
        pb2.FieldDescriptorProto.LABEL_REPEATED: "repeated"
    }

    type_map = {
        pb2.FieldDescriptorProto.TYPE_DOUBLE: "double",
        pb2.FieldDescriptorProto.TYPE_FLOAT: "float",
        pb2.FieldDescriptorProto.TYPE_INT64: "int64",
        pb2.FieldDescriptorProto.TYPE_UINT64: "uint64",
        pb2.FieldDescriptorProto.TYPE_INT32: "int32",
        pb2.FieldDescriptorProto.TYPE_FIXED64: "fixed64",
        pb2.FieldDescriptorProto.TYPE_FIXED32: "fixed32",
        pb2.FieldDescriptorProto.TYPE_BOOL: "bool",
        pb2.FieldDescriptorProto.TYPE_STRING: "string",
        pb2.FieldDescriptorProto.TYPE_BYTES: "bytes",
        pb2.FieldDescriptorProto.TYPE_UINT32: "uint32",
        pb2.FieldDescriptorProto.TYPE_SFIXED32: "sfixed32",
        pb2.FieldDescriptorProto.TYPE_SFIXED64: "sfixed64",
        pb2.FieldDescriptorProto.TYPE_SINT32: "sint32",
        pb2.FieldDescriptorProto.TYPE_SINT64: "sint64"
    }

    def decompile(self, file, out_dir=".", stdout=False):
        data = file.read()
        file.close()
        descriptor = pb2.FileDescriptorProto.FromString(data)

        self.out = None
        if stdout:
            self.out = sys.stdout
        else:
            out_file_name = os.path.join(out_dir, descriptor.name)
            out_full_dir = os.path.dirname(out_file_name)
            if not os.path.exists(out_full_dir):
                os.makedirs(out_full_dir)
            self.out = open(out_file_name, "w")
            print(out_file_name)

        self.indent_level = 0
        self.decompile_file_descriptor(descriptor)

    def decompile_file_descriptor(self, descriptor):
        # deserialize package name and dependencies
        self.write('syntax = "proto2";\n')
        if descriptor.HasField("package"):
            self.write("package %s;\n" % descriptor.package)

        for dep in descriptor.dependency:
            self.write("import \"%s\";\n" % dep)

        self.write("\n")

        # enumerations
        for enum in descriptor.enum_type:
            self.decompile_enum_type(enum)

        # messages
        for msg in descriptor.message_type:
            self.write("\n")
            self.decompile_message_type(msg)

        # services
        for service in descriptor.service:
            self.write("\n")
            self.decompile_service(service)

    def decompile_message_type(self, msg):
        self.write("message %s {\n" % msg.name)
        self.indent_level += 1

        # deserialize nested messages
        for nested_msg in msg.nested_type:
            self.decompile_message_type(nested_msg)

        # deserialize nested enumerations
        for nested_enum in msg.enum_type:
            self.decompile_enum_type(nested_enum)

        # deserialize fields
        for field in msg.field:
            self.decompile_field(field)
        if msg.name == 'EnumOptions':
            self.write('optional bool allow_alias = 2;\n')

        if not self.proto3:
            # extension ranges
            for range in msg.extension_range:
                end_name = range.end
                if end_name == 0x20000000:
                    end_name = "max"
                self.write("extensions %s to %s;\n" % (range.start, end_name))

        # extensions
        for extension in msg.extension:
            self.decompile_extension(extension)

        self.indent_level -= 1
        self.write("}\n")

    def decompile_extension(self, extension):
        self.write("extend %s {\n" % extension.extendee)
        self.indent_level += 1

        self.decompile_field(extension, True)

        self.indent_level -= 1
        self.write("}\n")

    def decompile_field(self, field, ext=False):
        # type name is either another message or a standard type
        type_name = ""
        if field.type in (pb2.FieldDescriptorProto.TYPE_MESSAGE, pb2.FieldDescriptorProto.TYPE_ENUM):
            type_name = field.type_name
        else:
            type_name = self.type_map[field.type]

        # build basic field string with label name
        field_str = "%s %s %s = %d" % ( (self.extension_label_map if ext else  self.label_map)[field.label], type_name, field.name, field.number)

        # add default value if set
        if not self.proto3 and field.HasField("default_value"):
            def_val = field.default_value
            # string default values have to be put in quotes
            if field.type == pb2.FieldDescriptorProto.TYPE_STRING:
                def_val = "\"%s\"" % def_val
            field_str += " [default = %s]" % def_val
        field_str += ";\n"
        self.write(field_str)

    def decompile_enum_type(self, enum):
        self.write("enum %s {\n" % enum.name)
        self.indent_level += 1

        all_vals = []
        for value in enum.value:
            if value.number in all_vals:
                self.write("option allow_alias = true;\n")
                break
            all_vals.append(value.number)
        if self.proto3:
            first_val = all_vals[0]
            if first_val != 0:
                prefixes=enum.value[0].name.split('_')
                prefixes.pop(len(prefixes)-1)

                prefix ='_'.join(prefixes)

                self.write("%s = %d;\n" % (prefix+"_DEFAULT", 0))

        # deserialize enum values
        for value in enum.value:
            self.write("%s = %d;\n" % (value.name, value.number))

        self.indent_level -= 1
        self.write("}\n")

    def decompile_service(self, service):
        self.write("service %s {\n" % service.name)
        self.indent_level += 1

        for method in service.method:
            self.decompile_method(method)

        self.indent_level -= 1
        self.write("}\n")

    def decompile_method(self, method):
        self.write("rpc %s (%s) returns (%s);\n" % (method.name, method.input_type, method.output_type))

    def write(self, str):
        self.out.write("\t" * self.indent_level)
        self.out.write(str)
