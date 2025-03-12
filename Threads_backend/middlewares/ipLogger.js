import IpAddress from '../models/ipModel.js'; // Adjust the path as necessary

const ipLogger = async (req, res, next) => {
    const ip = req.headers['x-forwarded-for']?.split(',')[0] || req.connection.remoteAddress;

    // Store the IP address in the database 
    try {
     
        const newIp = new IpAddress({
            ipAddress: ip,
            userId: req.user ? req.user._id : null, // If you have user info in req.user
        });
        await newIp.save();
        console.log('IP address stored successfully:', ip);
    } catch (err) {
        console.error('Error storing IP address:', err);
    }

    next();
};

export default ipLogger;