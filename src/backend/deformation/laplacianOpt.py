import torch
from scipy.spatial import KDTree
import numpy as np

# # 定义函数来计算点集B中每个点的移动距离之和
def compute_distance_loss(Binit, B):
    return torch.sum(torch.norm(Binit - B, dim=1))

def compute_diff(A, B, k=4):
    Anumpy = A.numpy()
    tree = KDTree(Anumpy)
    dist, idx = tree.query(A, k)
    dist[np.isclose(dist, 0)] = np.inf
    e = 2
    W = 1 / (dist ** e) 
    W = W / np.expand_dims(W.sum(axis=1), axis=-1)
    lprime = torch.sum(torch.tensor(Anumpy[idx] * np.expand_dims(W, axis=-1), dtype=float), dim=1) - A
    l = torch.sum(torch.tensor(B.detach().numpy()[idx] * np.expand_dims(W, axis=-1), dtype=float), dim=1) - B
    return torch.sum(torch.norm(lprime - l, dim=1))
    


def optimize_points(A, B, alpha = 100, k=5, num_iters=50, lr=0.1):
    # Convert point sets to tensors
    A = torch.tensor(A, dtype=torch.float)
    Binit = torch.tensor(B, dtype=torch.float)
    B = torch.tensor(B, dtype=torch.float, requires_grad=True)

    # Initialize optimizer
    optimizer = torch.optim.Adam([B], lr=lr)

    # # Compute nearest neighbors in A for each point in B
    # tree = KDTree(A.numpy())
    # _, idx = tree.query(A, k=2)
    # nn_A = torch.tensor(A[idx[:, 0]])

    # # Compute nearest neighbors in B for each point in B
    # _, idx = tree.query(B.detach().numpy(), k=2)
    # nn_B = torch.tensor(B[idx[:, 0]])

    # Optimization loop
    for i in range(num_iters):
        ## Compute displacement vectors from nearest neighbors
        # disp_A = nn_A - A
        # disp_B = nn_B - B

        # # Compute cosine similarity between displacement vectors
        # cos_sim = torch.sum(disp_A * disp_B, dim=1) / (torch.norm(disp_A, dim=1) * torch.norm(disp_B, dim=1))

        # Compute loss as sum of point movement distances and cosine similarities
        loss1 = compute_diff(A, B, k)
        loss2 = compute_distance_loss(Binit, B)
        loss = alpha * loss1 + loss2
        
        # loss = torch.sum(torch.norm(disp_B, dim=1)) - torch.sum(cos_sim) + 1.5 * compute_distance_loss(Binit, B)

        # Zero gradients, perform backward pass, and take optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(loss1, loss2)

    return B.detach().numpy()

def get_opt_coords(new_coords, alpha = 100, k=5, num_iters=100, lr=0.1):
    A = []
    for i in range(len(new_coords[0]) // 2):
        A.append((new_coords[0][2 * i], new_coords[0][2 * i + 1]))
    nnew_coords = [new_coords[0]]
    for j in range(1, len(new_coords)):
        each = new_coords[j]
        B = []
        for i in range(len(each) // 2):
            temp = []
            B.append((each[2 * i], each[2 * i + 1]))
        cur = optimize_points(A, B, alpha, k, num_iters, lr)
        for point in cur:
            temp.append(round(point[0]))
            temp.append(round(point[1]))
        nnew_coords.append(temp)

    return nnew_coords