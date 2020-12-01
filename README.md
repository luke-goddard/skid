# SKID Fuzz (Structured Kernel Ioctl Driver Fuzzer)

Skid expands on the work behind [Difuze](https://acmccs.github.io/papers/p2123-corinaA.pdf). Difuze is an interface aware fuzzer for the [ioctl](https://man7.org/linux/man-pages/man2/ioctl.2.html) syscalls. Vendors adding new custom code to the kernel will always pose a risk, but pair that risk with a direct interface to the kernel's new code from userland and you're left with a profitable target for bug hunting. On android 63% of kernel related bugs are using ioctl on vendor's custom drivers, see [here](https://events.static.linuxfound.org/sites/events/files/slides/Android-%20protecting%20the%20kernel.pdf).

```
                  ████████████████████████████████████
                ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒████
              ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██████      
            ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████      
            ██▒▒▓▓████████████████████████████▒▒▓▓██████
            ██▒▒▓▓████████████████████████████▒▒▓▓██████
            ██▒▒▓▓████████████████████████████▒▒▓▓██████
            ██▒▒▓▓xxxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████
            ██▒▒▓▓ ███████╗██╗  ██╗██╗██████╗ ▒▒▓▓██████
            ██▒▒▓▓ ██╔════╝██║ ██╔╝██║██╔══██╗▒▒▓▓██████
            ██▒▒▓▓ ███████╗█████╔╝ ██║██║  ██║▒▒▓▓██████
            ██▒▒▓▓ ╚════██║██╔═██╗ ██║██║  ██║▒▒▓▓██████
            ██▒▒▓▓ ███████║██║  ██╗██║██████╔╝▒▒▓▓██████
            ██▒▒▓▓ ╚══════╝╚═╝  ╚═╝╚═╝╚═════╝ ▒▒▓▓██████
            ██▒▒▓▓ xxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████
            ██▒▒▓▓████████████████████████████▒▒▓▓██████
            ██▒▒▓▓████████████████████████████▒▒▓▓██████
            ██▒▒▓▓████████████████████████████▒▒▓▓██████      
            ██▒▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓██████
            ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████████  
            ██████████████████████████████████████████████▓▓██
            ████████████████████████████████████████████▓▓████
        ██████████████████████████████████████████████▓▓██████
      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████████
      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████
      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████████████▓▓▓▓████████
      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████████████▓▓▓▓████████
      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓████████
      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████
      ████████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒▒▒██████  
    ██▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████████    
  ██▒▒██████████████████████████████████████████████████      
██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓████        
██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████          
  ████████████████████████████████████████████████
```

## SKID's improvements

* No compilation required to model code
* Less setup time
* Less dependencies
* More generic, not just android but all Linux Kernel's
* Defines structure using [protobuf](https://github.com/protocolbuffers/protobuf) allowing the use of google's new [protobuf-mutator](https://github.com/google/libprotobuf-mutator)
* Moduler
* Has ASCII art

## Problems with coverage guided fuzzing

SKID is __not__ a coverage based fuzzer. Coverage based fuzzers such as AFL are undoubltly powerful but require either instrumentation or emulation. Since device drivers often talk to FPGA's and custom hardward emulation is not really an option. Kernel coverage with [kcov](https://www.kernel.org/doc/html/latest/dev-tools/kcov.html) would require the kernel to be recompiled. This could be a feature for the future.

> Coverage-guided mutation-based fuzzers, such as libFuzzer or AFL, are not restricted to a single input type and do not require grammar definitions. Thus, mutation-based fuzzers are generally easier to set up and use than their generation-based counterparts. But the lack of an input grammar can also result in inefficient fuzzing for complicated input types, where any traditional mutation (e.g. bit flipping) leads to an invalid input rejected by the target API in the early stage of parsing.

## Interface Recovery

The Difuze project chose to use [LLVM Bitcode](https://llvm.org/docs/BitCodeFormat.html) produced by clang and then convert it to XML to model the code's functions and data structures. The problem with this approch is that some code is hard to compile with the __correct__ toolchain, [nevermind the incorect toolchain](https://lwn.net/Articles/734071/). This limits the number of projects that Difuze can be run against. Skid uses [Doxygen](https://www.doxygen.nl/index.html) to extract the code structure from undocumented C code and document the structure in XML. This verbose XML is boiled down to [protocol buffers](https://github.com/protocolbuffers/protobuf). Doxygen is both older and more mature than me while still being activly maintained. This aproach requires much less headache, but give us less control over the C preprocessor.
