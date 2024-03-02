import os, sys
import tarfile
import shutil
from tempfile import TemporaryDirectory
import PySimpleGUI as sg

def MainWindow():
	layout = [
		[sg.Text("Package(s) to Extract"), sg.Input(k="packages"), sg.FilesBrowse("Browse", file_types=(("*.unitypackage", "Unity Package Files"), ("*.* *", "All Files")))],
		[sg.Text("Extract Location"), sg.Input(k="dirout"), sg.FolderBrowse()],
		[sg.Button("Start"), sg.Cancel()],
		[sg.Text("Running...", k="running", visible=False)],
	]
	win = sg.Window("Unity Package Extractor", layout)
	while True:
		event, values = win.read()
		if event in (sg.WIN_CLOSED, "Cancel"):
			return
		elif event == "Start":
			if ";" in values["packages"]:
				pks = values["packages"].split(";")
			else:
				pks = [values["packages"]]
			if len(values["dirout"]):
				dout = values["dirout"]
			else:
				ErrorWindow("Extract Location must be set.")
				continue
			win["running"].update(visible=True)
			win.read(0)
			for pk in pks:
				ExtractPackage(pk, os.path.join(dout, os.path.basename(pk).rsplit(".", maxsplit=1)[0]))
			win.close()
			InfoWindow("Done!")
			return

def InfoWindow(text, title="Info"):
	return sg.Window(title, [(sg.Text(s) for s in text.split("\n")), [sg.Ok()], [sg.Sizer(100, 0)]]).read(close=True)

def ErrorWindow(text, title="Error"):
	return InfoWindow(text, title)

def ExtractPackage(fname, dname):
	try:
		zf = tarfile.open(fname)
	except Exception as e:
		return ErrorWindow(f"Error opening Unity Package {fname} as archive.\nOriginal Error:\n{str(e)}")
	with TemporaryDirectory(prefix="PyUnityPackageExtractor") as d:
		zf.extractall(d, [f if not f.name[1] == ':' or f.startswith("/") else None for f in zf.getmembers()])
		zf.close()
		try:
			os.mkdir(dname)
		except:
			pass
		try:
			os.mkdir(os.path.join(dname, "Assets"))
		except:
			pass
		for root,dirs,files in os.walk(d):
			for dn in dirs:
				with open(os.path.join(root, dn, "pathname")) as f:
					pathname = f.read()
				try:
					os.makedirs(os.path.join(dname, os.path.dirname(pathname)))
				except:
					pass
				try:
					shutil.copyfile(os.path.join(root, dn, "asset"), os.path.join(dname, pathname))
				except:
					pass
				shutil.copyfile(os.path.join(root, dn, "asset.meta"), os.path.join(dname, pathname+".meta"))
			break

ICON_DATA = b"iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAAAXNSR0IArs4c6QAAHgJJREFUeJztfX10FNX9/nNndnazyeY9IYSFxLyRAOFF8a1iqZ4jrdqKp+f0COhXIkUUwR4Eij+oCLYiUqiCQIUDAkFOlQoUeyhoQQQp2qLVQoAEQggESEgCedvdZN9m5v7+2NzJ7O5sskkWgu4+5+RkdmZ27ux8nvt5u597h1BKKSIIW3B9fQMR9C0iBAhzRAgQ5ogQIMwRIUCYI0KAMEeEAGGOCAHCHBEChDkiBAhzRAgQ5ogQIMwRIUCYI0KAMEeEAGGOCAHCHBEChDkiBAhzRAgQ5ogQIMwRIUCYI0KAMEeEAGGOCAHCHBEChDkiBAhz6Pr6Bm4W2Aw4SilEUYTL5YLRaATP8318Z32LHzwBKKWQZRltbW1obW2Fw+HAhQsXcPz4cRQVFSEpKamvb7FP8YMjgFrgbW1tEEURVqsVf//737Fr1y5UV1fD5XKhX79++OUvf4nExEQQQvr6tvsM32sCqNW6JEmwWCxwOBxoaWnBrl278Mknn+Dy5ctwu92KBpBlGQBgNBrR1tYGSmmEAN8XUEoVocuyDIvFArvdDkmSUF1djZUrV+Lrr7+G0+lEa2sr2traIEmS5rXsdju+/PJLZGRkwGQy3cyfcUvhe0MASZJgs9nQ2toKURRRX1+P4uJifPrpp4qgW1pa4HQ6g7qezWbDP//5Tzz22GMRAtxqYGpakiQ0NTXB5XLBZrNh+/bt2LdvH65evQq32w2r1Yq2trYeteFwOHDixAk4HI6wNgO3DAFkWYYoimhubobL5YLb7UZdXR0WLVqEM2fOwO12d6nWuwun0wmbzQZZlsM2HLwlCCCKIq5evYqKigqsWrUKJ0+ehNPphCRJaGxshNvtviHtWq1W7N69GwMHDkRCQsINaeNWB+nrNYIkScL58+cxceJEXLlyBS0tLXC5XDelbUIIhg4dir179yIjIyMszUCfagBKKaxWKzZt2oTy8nK0trb2SfuiKN7Udm8l9OlYgCRJuHLlCnbs2NFjZ47BaDQiNTW127ZckiQ0NDSEzK/4vqHPCEApRXNzM5YuXYqamhp0xxIRQhATE4P+/fvDbDYjOzsbEydOxMaNG9GvX79u3YfVasWePXtgtVq7+xN+EOgzE8CSN0ePHg0qduc4DsnJyRAEATExMXj88ccxadIkJCcng+d5EELwzTffdLsn22w27NmzB88++ywSEhJuuB+gTmbdLPdL/Zs4zrvP9wkBZFlGQ0MD5s6di9raWs1zBEFAUlISdDodCCFISkrCsmXLkJ+fD0EQYDKZEBsbC57nQSlFRUUFXnvtNVy/fr3b99Lc3HzT/ABKKZxOJ2RZgtvtAm4CCXQ6HQS9AYKg9z8WyoYYux0Oh6JSCSHgOA4cxynbsiyjsrISp0+fVkI8QogiVJ1Oh5ycHCxZsgQDBgwAx3HgeR4pKSkQBMGvl1qtVvzjH/9AVVWVkkRSg+d5JCYmoqmpSVNDiKKIa9euISMjA4IghPKR+EGWZVy/Xg+3ywFXWyNk2Q2Atv/5wlcbEXj/dKJ9mtcOAkNUDJKS0yEkpPq1EDICMOFbrVYcOHAA7733nmKrY2NjYTKZEBMTg5iYGLhcLnz00UcQRRFms1k5b+LEiXjiiSdgMpkgCAJSUlIU9Q7AT/BsEKiiogIbNmxAS0uL331xHIe8vDwsWLAA8+fPx9WrV/3OaWxsxKpVq/DOO+8gLS0tVI9EE6LoQk1VKYhsRU6/RsB1DVRyg8pOAB5yEkLa/7j2zxzA9oHzkIDzbIMAIAQcIQD7g/f5VjEeAr0XwA0mgM1mw6effor58+ejurpa+SFMA6i1gNlsxrJlyzB27FgYDAZwHKdoAGangrHHtbW1mDt3Ls6fP69pUxMTEzF79myMGjUKer2/CgQ8A0Pffvst7Hb7TUgLU4iiCzqIMEQZwQlxkEQ7JJcI6m4F0wQc0C5sfxJwbB/HSEIAwnXYd8IBhGvnAwFxUFCqnVsJCQEopbDb7Th48CDmz5+PqqqqgA4Ox3EYPnw4iouLkZubi+joaIUo3YXb7UZ5eTnKy8s1bTjP88jMzMSDDz6o+BSXL1/WNBMul+smEaBdKODB8wQcF+MRmOyGKNoBKoGgw0xRUBAQALSdGwQU1NPzKfG2ApR2aH9K0WEvJEDjNwO9DANZ8UVrays+//xzzJ07t0vhDx06FJs3b8awYcMQExOjaIWetH316lX89re/RV1dneY5AwYMwMqVK5GZmYnk5GQ899xzSExM1DzXbrfjv//9r0KCYMBGIHuWQ/AISKc3QYhKgt40EEKMGbwxFYSPAsAprgFFe+RAKUDldnPLLsP8B7n9j6r+s8Mdn33RYwIwm9/W1ob9+/dj1qxZuHjxYpfCLy4uxvDhwxXvvqdtO51OHD9+HNXV1Zo9Wq/XY/jw4cjJyVFCx5/85CeIjo7WvKbFYsHOnTthsViCugdRFFFeXo61a9fi/PnzPY4iCAE4jgfH68Eb4sDr48EJcSAQoHRnrUfKCKF5gjrMDORgetBjE8CE/9lnnwXd899//30UFhb2SviAx5M+d+4cXn31Vc2wjxCCQYMG4Q9/+APS0tKUtoxGI4xGo+Y1nU4nTp8+DYfDEdQ91NbWoqioCBUVFfjiiy9QXFyM9PT0bv4uj3AIATieh45LgCyIkHkDJCpDFi3tqpz1YEYIj/ag7dueJiko9ZgKAgIQJovO76dHGoDZ/CNHjmDOnDlBCX/Tpk0YNmxYr4VPKUVTUxPeeecdVFRUaPb+mJgYPProo8jMzPRKDUdHR+NHP/pRQC3gcrm8ysY6gyRJqK2tRVNTE06dOoWzZ8/C7XZ3O7nT4bzL4DkKHa+DYEyBEJcDPioNXFSKR9iKCVD3alXvVisDqt7f+f10mwDqnv/iiy92qfaHDBmC4uJijBo1SjOG727boijiwoULOHjwIOx2u2abWVlZir1Xh5CxsbF4/PHHERsbq3n9trY2HDt2TPO6viCEKDmDuro6zJo1CyUlJT0eU/DcpQxCPE4ox+vBCSZwfLSXL6BAZQIoDaDkg+BitwjAhH/gwAHMnj27S+EXFBRg8+bNGD58eK+Fz1BfX4958+bhypUrmseTk5Mxb948ZGVl+aU9DQYDhg0bBoPBoPndpqYmrF69Go2NjV325KioKNx1112IioqCLMsoLS3FtGnTcPLkya79gUBmmcoAFUGoExyvAx+dBj46DQDvQwLqfTGFARTwOuqjHTQQNAHUPf+ll17qUvj5+fnYsmVLSHo+a5/1/kBhn06nQ25uLsaMGQOj0ejXJsdxiIqKQkJCgh85gO6lhZOSkvDKK69g2LBh4HkekiTh5MmTmD59Oq5evRqkKfAWJIEnyCMQQeAEz+vB8QYlAvREA6ptRfgez59S2qEl/EyFNoIiABP+wYMHMWvWLFy6dKlT4efl5WHjxo0YOXJkyHo+pRTV1dWYPXs26uvrNc/p378/3n77bQwaNChgm/Hx8Zg0aRLi4uI0j8uyHDBlrIZOp8OQIUOwfv165Ofng+M4SJKECxcuoKSkJOjiVG+oBSaBUJlF/T7nsM0O3a8eZPLTEJ2gUwKwON9ut+PAgQP4zW9+06nwCSHIysrCmjVrMHr0aOj1+pAJ3+l04tixY7h48aKmcARBQEFBATIyMjp1NE0mEx555JGAlcDNzc3Ytm2bZlrZF4wEc+fOVVLIDQ0NmD9/PkpLS4MMDdU9lOl5zx/r6Z5DKgH7PX8fUqiu1ZUeCkgA9cDOoUOHMGvWLFy+fLnLnr98+XLcd999MBgMIcuosbKxJUuWoLGx0e84C/vefPNN9OvXr9N2OY5DXFxcwHCwtbUVBw4cgM1mC0qNG41G/PSnP8VDDz0Eo9EIWZZRVlaGqVOnoqSkJAAJfLx3tXev/k+ldr+gPclD4RMNMLNAva+jJopX5KDxPAL9MCb8w4cPY8aMGV32/JycHLz//vt4+OGHlfRuKEApRUtLC1atWoXz589rhmjR0dEYN24cbrvtti4rggghiI6OxujRoxEVFaXZXmtra9DePMdxSE9Px8svv4yhQ4cq/sCpU6cwc+ZMXLp0Kaiw0k/4kDWEp3L3vRJB8D5H69qB7t/v1Pae73Q6cfjwYbzwwgu4dOlSwAsQQnDbbbdh5cqVGDlypKbz1RuIoojKyspOw77s7GzMmDEj6IKO+Ph4PPXUU5qVwDqdDmazOeDAkRZ4nkdBQQE2bNiA4cOHg+d5iKKIs2fPKhNXtKEhGL9dLNRj6pwq2/5KXvUpyHyEFwHUav/IkSOYPn16l8IfNGgQlixZgrFjx4bM5qvvp66uDjNnzsTly5c1z0lOTsbvfvc75ObmBl0PqNfrkZeXpylks9mM5cuXd2lKfKHT6TBixAhs2LBBqTBubm7G6tWrcebMmU78ASW+U+3yTvhQlWZQ9IGP2+AV/FEWI3QdCfgRwOVy4d///jemTZsW8KEzpKamYuHChXjooYeg0+ngcrngcDhC9mez2VBeXo6qqipNlazT6VBQUIB77723W5qHEAKDwYDY2Fiv7xgMBtxxxx3IysrqUWEIK2R57LHHEBsbq1QqPffccygrK+vCrHgL3fNZ1jABHbbfq5dT32v5X17znpXjlMLtduPYsWN45plnuhS+IAh48MEHER0djWPHjt2QIdTm5mYsW7YMDQ0NmsfT0tLwpz/9SSkq6Q5iY2Pxs5/9DJcuXYLValUimIULF3a7sFSN+Ph4zJw5E2fPnsWhQ4fgcrlQWlqKxYsX4+2330a/fildXMHXljMT0J4tJB7hE/VAEfH5ejcehc5zcU+S5T//+Q8mT57cpfABz1j8vn37cPjw4eBb6yZY7aCWE8WSPgMHDoRO170xLZYWHj9+PLZv3w6r1Yr4+HhMmDABBoMhqN/fGTiOwwsvvIBvv/0W169fh9PpxL/+9S/s3LkTRZP/T3Wmr9Mnw18DdCR4iPIdonj/xGvQp136FJ7BIMr2BYYO8IRZ//vf//D0009368dbrdY+KadmjueKFSuQmpraI+0jCILi7PE8j5ycHIwZM6bLiCdYiKKIpqYm5XNDQwM2bNiAu+4cDSKK0OnQLud2oTMSAOgggdzh/DF5AiBexR5QfUdVOKIqFunMIdQBQGVlJX71q1/1mvk3CyaTCRMmTEBubm63e78aBoMBqampcLvdWLhwIaKiolBZWRlwnKE3oJSisrISc+bMxsL/9wLMaXHwdtB8E0Lo2OfrIBLS/r/DMQQh/po/CBJzALB58+Zul1P3JaKionDPPfcETOYEA0IIdDod0tLSlPGBs2fPBl0P0BOwlLp2oYaPo6doBI1qHiXR4+/7qeJA1QGPZqBUhizLXtpNBwCzZs1CdXU1du7ceUMfQKjQ2NiI3//+9ygoKEBOTk6PS8qcTifKy8tRW1uL4uJiTJ06FdnZ2ZBlOcjkTWDIsgyr1er1sJmfYYphaWhm9wF/MnQQwSsQ8K31UGl+ZZ8PdAKBLLvgsLciymgCaa8vIIR4CJCWloY//vGPaG1txSeffBI0CUI10BMILDLxBRt0+fzzz5Geno6YmJhu3wdbSMput6O1tRVHjhxBUVER1q1bhy+//DKomoBAcLvdKC0txccff6wkgdjw8YQJE9BYVw5AfX2NENDLGYSmd8/cwQ7ngO1t/9BuLnQ8IIt2uO1NMBiiIVGq1GLqAI867N+/P9asWYMXX3wRBw4c6HKmLnPEfKtuQgm3242ysjLU1dX59UiWZLn33nuVSqPuwG634+jRo4qALl++jEWLFqG4uBhFRUU9dgJFUcSJEyewefNmhUSCIGDMmDF46623kJGRgab6io4vaFkBrx2+6h9eRGBZAaL6pPL+AAAGnkIUL0N2OGCz6MDxAkxxnjkCCgEAID09HWvWrMHixYuxffv2TmfsUkrR0NCAtWvXYsiQIT2u7u0MLpcLR48exUsvveSXC5BlGRcvXsTq1auxbNkypKSkBN0+G1/YuXOnEsWIoojz58+jrKwMZrO5R4NZoiiipKTEq0aS53mMGDECb731FgoKCiCK6mFiX19A9t+nzvUo9X8E/mpBBptNoN7r+Y4EQa4HpBbUVcsQDAkwxT0IQJUIYj92wIABeP3119HW1obdu3d3Oq7d3NyM2bNn4y9/+UtI6v18Icsy7r//fmRmZqKpqclPC9jtdhw6dAgXL15EQkJC0O0zZ+z8+fNei1HU19dj0aJFyM7ORn5+frc0myiKKCsrw/Tp03Hy5ElIkgSO41BYWIgNGzYoz8ebAIFuUL2hjgiIzxa8jnn1f9VJniMSQN0QXTYQriMF7pUKZhM0+vfvj+XLl+OBBx4IWEAJeAR05swZPPnkkzhx4gREUex1/KwGx3FKbX///v39jlNKceXKFSxYsAC1tbVBty2KIq5cueJn5yVJQmVlJXbs2AGLxRL09SRJQlVVFRYvXuwl/KFDh2Lt2rVKJbTP3Xt7+l75gI48ABsVpD4Kgaqvo/HZry2IoNQFu60ezraOIXW/0UBGggEDBmD9+vUYP358pz1BlmWcPXsWkydPxunTp0NOAkEQkJeXh8LCQs38PHO4SktLg15LiE1k0fJzLBYLPvroIzQ3Nwd1LUmSUFNTgy1btuCLL76Aw+EAx3HIzc3FqlWrMHr06MDjCl5SVQlfGceXO+J8dh5F+zgA/J6zqiAM2kSQQWU3ZLljYEqzHoDN38vIyMCyZcuQl5fXqZOlJgErigwVCQghSElJwRtvvIH09HTNc+rr6/HKK6+gpqamy/CNUgqLxYK//e1vmllMNhoaDJgvsXHjRmzevFnJ/CUlJWHevHlK0ai/WfKJ+TuLAtr3e4/sqa6hBAnqpADb9iGYBikCFoQwTTBw4EDs3r0bd955Z5ckOH36NIqKikJOAp1Oh8zMTNx///2aRRySJOHSpUs4duxYl8Jj9j9QxY9er8fgwYMDVg6r4Xa7UVJSgg8++EAxQYIgYNSoURg3bhxMJlMnPomvsH2PsR7e4Rh21b97gk5rApkmyMvLw9atW3HPPfdoVtMysPLoyZMno7S0FJIkhYQEhBAkJiZi/vz5yM3N1byHhoYGLF26FOfOneu0Fs9ut+Obb74JGOcnJCTg2Wef7XIRaVEUcfLkSa8KaZ7nMWzYMKxYsQJms7nTZ9UBrZ7P4J2188v8hQBd3iEjQU5ODjZt2oTBgwd3SYKysjIUFRWF1CfgeR55eXl4/fXXkZycrNnuuXPnsHTpUjQ0NARss6WlBR988EHAok+DwYDCwsIuNUBdXR1mzJiBU6dOQZIk8DyP4cOHY9OmTQGcvgDQUgBspFemoFTCDZF8O4IqC2ckyM3Nxa5du5RlWgJBlmWcOnUKzzzzTMjMASviuP322zFo0CBNx9ThcODYsWOoqqrSbJMVvFRUVARci9BoNAaVA2CLWzLhFxYW4r333sOIESO6Fj5Fh6Pna++V9C8Hl8MC0akRjWiGiZ02FvBo0BNDGAkGDx6MXbt2YezYsZ2SgE2UmDp1akjNQXp6eqcreVRXV2POnDmoqanxO8amsgcSPptBHBMTE9S9sKVrCgsLsXHjRowYMSLI3AFzztTCZwM/HptPZQl2Wx3s1jpQKvt9NRSglHZvahghBDzPY/DgwXj33XcxatSoTs0BI8G0adMUEvQGbD4eS9Ro9TRWRFpeXu4laLaCyb59+2Cz2TSvHxcXhyeeeAJxcXFdagC9Xo+CggLccccdWL9+PUaOHNnNRFgAr191v7Lkbl9DKPRgnbHbk0OZJsjOzsbWrVu7NAes2GTatGkoKyvr9WpchBD069cPK1asUGbk+KK+vh7z589HZWWlF+laWlqwffv2gGsACIKAzMzMoCqCU1NTsWXLFuzevVuJ9XudBfU1DbIIyDKoHLpurwSR7QXAPZoezjRBXl4edu3ahR//+MedPjRRFPHdd99hypQpyoyZ3pgDnucxZMgQvPrqq5rv/JEkCefOnUNxcTFaWlq8St0DrQpKCIHRaAy6HFyn0yE9PR1ms7kXwu8kAghhMs23TTbK2mMCAN4kWLduHUaPHt2p/RNFEcePH8evf/1rnD59ulfmgBCCqKgo3H333coycr6w2WzYvXs3Ll26BEmSIIoiqqqqAtp/k8mERx99tIvYPTQgHOf5I0TDR+vY4Zb0cIkC3LIeLsnz55b1cIoC3JIAl6iHQxLgFAW4RKFj2y3AIfFwiDo4RQEOUQeHm4fTpYMMAZTySgfs1SJRjATZ2dnYuHEjJkyYgDNnzgQUriRJOHHiBKZOnYrNmzdj6NChPS7pYmMWr732GqZPn+43YZRNJmWjhTzPY//+/QHtP5ssEh8f36P7Cf6+ecTEJoCTeciQQGFrH9NXjwQCMtWhxj0KbtF7AS1lm0N7ZTBp/8hGfohSPey10f49yRAHGhWnPPderxLGSJCfn48PP/wQU6ZMQUlJScC8PNMERUVF2LRpk7IWYHJysjKxJJgeyMLCUaNGwWw24/r1635p4La2Nhw+fBgXL15EUlIS9uzZE5AAer0eSUlJN/zFETzPIyUtG5K7FS1iFHS6q+CpAwRtILSj4wgGAwrvGg9wRmhU+3mjOwqLeJaeYw5ryN4XwBZtPHfuHJ5//nlcvHgxYF6e5dujoqLAcRxSUlKwdOlSFBQUeJY1FQQkJiYqtjUQIVhc//XXX+Opp57SLGrleR4jR47EkiVL8Pzzz2ueIwgCxo4di61bt2LAgAE31AR4Zlu3QRJdcLZdg166Ah4WGOVr4KgVij3gY4D+T4Pobuz7jEK2UKTaJ9i+fbuXo6euQWPO2Mcff4w33ngDFosFNTU1KCoqUkq0hwwZgjlz5iA3NxeCIMBgMPj1TiYkQRCQk5ODwsJC1NXV+dl4NrP4r3/9a0Dvn80R8J0pdCPAnE1J0oNSGZLdAUIFyJwDRLSDUBG+4aDv90N6P6HSAAzBXI5V84wfPx5nzpzx0xSCICAhIQGCIEAQBIwYMQKLFi1CamoqOI7zIwSbjfvkk0/izJkzmg/NaDQGXANw0KBB2LdvH4YMGXJT3h3EohJZliG67aCSA9TdAJ2jFJxkA6QmEKKHlDoR4GP8lssNJQn67JUxDocDe/fuxfTp07ssSVfbZ71ej9tvvx0LFixQXhARFxcHSik+/PBDLFy4MOBUskDIysrCZ599hqysrBuuAdRgRKBUhiSJaGmsBaRmRInnEIVraDU9DspFw2AwQKfTKUQIbpApOPTZ+wL0ej3uvvtu5Ofnd7kki8vl8lpWvqamBl999RV4nkdsbCymTJmCcePGIT8/P6hhXDV6Mh08VOjo1e1hGR8F0GhQLgaA1X+QmIZ+Gds+0wDMaSwpKcEvfvELzVW8gwGb5xcdHQ1KKa5fv96tHANzQCdNmtQnL5Bkj99jEiRIkgjRZYOB1kMUMgGi80o0hdoE9JkGYE6j2WxGQUEBrl271qM0MavwCXaJV19ER0fj/vvv77T28UbCV7CEcOC4eBAYoSMGACTkal+NPn1pFCGeN4GsWLECWVlZvZrn19P2o6OjQ76qSW/gGWHUgfDRnjWEb0C5vVd7N+zKQYIlkV5++WXcd999GDRoENLT0xEfH3/DWM9gMpnw85//PODKoTcbTAuo369wownQ5y+OBDqmadlsNmXd/j179qC4uFiZD9DU1NTDtfcCIz09HVu3blVeWhGOuCUIwNARFnkKNy0WC1wuF1paWvDmm28qr4Zn7yTq7dByRkYGDh482OMJpj8E3BLvDmZQe7ixsbFKZY4sy/jzn/8Mp9OpzOnbtm2bUgDKyNIdLhNClHcThavwgVuMAL5gPgAbLwA8ZEhPT8cjjzyivFF8//79ePfdd5W3d1gsli7Lw00mEx5++OE+Cf1uJdxSJiBYqGNnSj3vLrBYLHC73aiursa6devw1Vdfoa2tDS6XC1ar1W900mw2Y8eOHbjzzjtv+KvibmXc0hogENSxMwDllXSUUgwYMAAFBQVwOByw2+347rvvUFxcjJMnT8LtdivOpsFgQFpa2k0PPW81/GB+vTqESkpKUrSD2WzGAw88ALfbDavVir1792Lbtm0YOHBggGlb4YXvpQnoCdjom91uh9VqBc/zyqtpwxlhQwAGtf8Q6rz69xFhR4AIvNHnqeAI+hYRAoQ5IgQIc0QIEOaIECDMESFAmCNCgDBHhABhjggBwhwRAoQ5IgQIc0QIEOaIECDMESFAmCNCgDBHhABhjggBwhwRAoQ5IgQIc0QIEOaIECDMESFAmCNCgDBHhABhjggBwhz/H5dack8RfEiZAAAAAElFTkSuQmCC"

if __name__=='__main__':
	if len(sys.argv) <= 2:
		sg.set_global_icon(ICON_DATA)
		MainWindow()
	else:
		if len(sys.argv) > 3:
			o = sys.argv[2]
		else:
			o = os.path.join(os.path.dirname(sys.argv[1]), sys.argv[1].rsplit(".", maxsplit=1)[1])
		ExtractPackage(sys.argv[1], o)
