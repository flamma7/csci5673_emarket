# Copyright 2020 the gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

licenses(["notice"])  # 3-clause BSD

package(default_visibility = ["//visibility:public"])

load("@grpc_python_dependencies//:requirements.bzl", "requirement")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("//bazel:cc_grpc_library.bzl", "cc_grpc_library")
load("//bazel:grpc_build_system.bzl", "grpc_proto_library")
load("//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")

# The following three rules demonstrate the usage of the cc_grpc_library rule in
# in a mode compatible with the native proto_library and cc_proto_library rules.
proto_library(
    name = "product_proto",
    srcs = ["product.proto"],
)

cc_proto_library(
    name = "product_cc_proto",
    deps = [":product_proto"],
)

cc_grpc_library(
    name = "product_cc_grpc",
    srcs = [":product_proto"],
    grpc_only = True,
    deps = [":product_cc_proto"],
)

py_proto_library(
    name = "product_py_pb2",
    deps = [":product_proto"],
)

py_grpc_library(
    name = "product_py_pb2_grpc",
    srcs = [":product_proto"],
    deps = [":product_py_pb2"],
)

proto_library(
    name = "customer_proto",
    srcs = ["customer.proto"],
)

cc_proto_library(
    name = "customer_cc_proto",
    deps = [":customer_proto"],
)

cc_grpc_library(
    name = "customer_cc_grpc",
    srcs = [":customer_proto"],
    grpc_only = True,
    deps = [":customer_cc_proto"],
)

py_proto_library(
    name = "customer_py_pb2",
    deps = [":customer_proto"],
)

py_grpc_library(
    name = "customer_py_pb2_grpc",
    srcs = [":customer_proto"],
    deps = [":customer_py_pb2"],
)
