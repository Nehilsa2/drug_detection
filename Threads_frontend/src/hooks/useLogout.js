import userAtom from "../atoms/userAtom";
import { useSetRecoilState } from "recoil";
import useShowToast from "./useShowToast";
import keys from keys.json

const backend = keys.backend;

const useLogout = () => {
	const setUser = useSetRecoilState(userAtom);
	const showToast = useShowToast();

	const logout = async () => {
		try {
			const res = await fetch(`${backend}/api/users/logout`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
			});
			const data = await res.json();

			if (data.error) {
				showToast("Error", data.error, "error");
				return;
			}

			localStorage.removeItem("user-threads");
			setUser(null);
		} catch (error) {
			showToast("Error", error, "error");
		}
	};

	return logout;
};

export default useLogout;
