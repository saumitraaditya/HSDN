pragma solidity ^0.4.17;

contract Computing_resource{
    
}

contract Networking_Delegation{
    string social_domain;
    address manager;
    mapping (address => bool) white_listed;
    
    event dns_path_installation(
        address initiator,
        string dns_target,
        string from_domain,
        string to_domain);
    
    modifier canInstall() {
        require (white_listed[msg.sender] == true,
        "Not allowed to install network rules.");
         _ ;
    }
    
    modifier canCall(address caller){
        require (msg.sender == caller,
        "Not allowed to call this method.");
        _ ;
    }
    
    constructor (string  _social_domain) public payable {
        social_domain = _social_domain;
        manager = msg.sender; 
    }
    
    function whiteList(address delegated_to)  public 
    canCall(manager) {
        white_listed[delegated_to] = true;
    }
    
    function install_dns_path (string dns_target, string from_domain,
    string to_domain) public
    canInstall(){
        emit dns_path_installation(
            msg.sender,
            dns_target,
            from_domain,
            to_domain
            );
    }
    
    function register_network(address delegate_to) public {
        locate_missing_cat(delegate_to).register_networking_delegates(social_domain);
    }
}

contract locate_missing_cat{
    address Initiator;
    mapping (address => Resource) resources; 
    mapping (string => address) networking_delegates;
    /// since we cannot iterate over keys of a mapping we need to maintain
    /// arrays of resources and networking delegates.
    address[] resource_addresses;
    address[] network_addresses;
    uint num_computing_resources;
    
    modifier canCall(address caller){
        require (
            msg.sender == caller,
            "caller not authorized.");
        _;
    }
    
    struct Resource{
        address resource_address;
        string social_domain;
        string resource_type;
        /// start of resource reservation interval.
        uint res_start;
        /// reservation interval.
        uint res_interval;
    }
    
    constructor () public payable {
        Initiator = msg.sender;
        num_computing_resources = 0;
    }
    
    function Register_computing_resource(string social_domain, uint res_interval) public {
        num_computing_resources = num_computing_resources + 1;
        resource_addresses.push(msg.sender);
        resources[msg.sender]  =  Resource(msg.sender, social_domain,
            "compute", now, res_interval);
    }
    
    function register_networking_delegates(string social_domain) public {
        network_addresses.push(msg.sender);
        networking_delegates[social_domain] = msg.sender;
    }
    /// Install dns resololution path on a social domain.
    function dns_resolution_flow(string dns_target, string social_domain, string from_domain, string to_domain) public payable
    canCall(Initiator) {
        address socialDomain = networking_delegates[social_domain];
        Networking_Delegation(socialDomain).install_dns_path(dns_target, from_domain, to_domain);
    }
}
